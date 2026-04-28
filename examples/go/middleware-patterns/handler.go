package function

import (
	"context"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

// Response represents the function response structure
type Response struct {
	Message   string      `json:"message"`
	Data      interface{} `json:"data,omitempty"`
	RequestID string      `json:"request_id,omitempty"`
	Timestamp string      `json:"timestamp"`
}

// RequestContext holds request context data passed through middleware chain
type RequestContext struct {
	RequestID   string
	StartTime   time.Time
	AuthUser    string
	Path        string
	Method      string
	RemoteAddr  string
	UserAgent   string
}

// Middleware type represents a middleware function
type Middleware func(http.Handler) http.Handler

// Logger middleware logs request details
func Logger() Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			start := time.Now()
			
			// Generate request ID
			requestID := fmt.Sprintf("%d", start.UnixNano())
			
			// Create request context
			ctx := context.WithValue(r.Context(), "requestID", requestID)
			ctx = context.WithValue(ctx, "startTime", start)
			
			// Log request
			log.Printf("[%s] %s %s from %s", requestID, r.Method, r.URL.Path, r.RemoteAddr)
			
			// Call next handler
			next.ServeHTTP(w, r.WithContext(ctx))
			
			// Log completion
			duration := time.Since(start)
			log.Printf("[%s] Completed in %v", requestID, duration)
		})
	}
}

// Auth middleware validates authentication token
func Auth(token string) Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			// Skip auth for health check, root path, and panic endpoint
			if r.URL.Path == "/health" || r.URL.Path == "/" || r.URL.Path == "/panic" {
				next.ServeHTTP(w, r)
				return
			}
			
			// Get auth header
			authHeader := r.Header.Get("Authorization")
			if authHeader == "" {
				http.Error(w, "Authorization header required", http.StatusUnauthorized)
				return
			}

			// Debug logging (only in DEBUG mode)
			if os.Getenv("DEBUG_MODE") == "true" {
				log.Printf("Auth Debug - Expected token: '%s', Auth header: '%s'", token, authHeader)
			}
			
			// Validate Bearer token
			parts := strings.Split(authHeader, " ")
			if len(parts) != 2 || parts[0] != "Bearer" || parts[1] != token {
				http.Error(w, "Invalid authorization token", http.StatusUnauthorized)
				return
			}
			
			// Add user info to context
			ctx := context.WithValue(r.Context(), "authUser", "authenticated-user")
			next.ServeHTTP(w, r.WithContext(ctx))
		})
	}
}

// Recovery middleware handles panics
func Recovery() Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			defer func() {
				if err := recover(); err != nil {
					log.Printf("Panic recovered: %v", err)
					http.Error(w, "Internal Server Error", http.StatusInternalServerError)
				}
			}()
			next.ServeHTTP(w, r)
		})
	}
}

// CORS middleware adds CORS headers
func CORS() Middleware {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Access-Control-Allow-Origin", "*")
			w.Header().Set("Access-Control-Allow-Methods", "GET, POST, PUT, DELETE, OPTIONS")
			w.Header().Set("Access-Control-Allow-Headers", "Content-Type, Authorization")
			
			if r.Method == "OPTIONS" {
				w.WriteHeader(http.StatusOK)
				return
			}
			
			next.ServeHTTP(w, r)
		})
	}
}

// ApplyMiddleware applies middleware chain to a handler
func ApplyMiddleware(h http.Handler, middleware ...Middleware) http.Handler {
	for i := len(middleware) - 1; i >= 0; i-- {
		h = middleware[i](h)
	}
	return h
}

// Main application handler
func appHandler(w http.ResponseWriter, r *http.Request) {
	// Get request context
	requestID, _ := r.Context().Value("requestID").(string)
	startTime, _ := r.Context().Value("startTime").(time.Time)
	authUser, _ := r.Context().Value("authUser").(string)
	
	w.Header().Set("Content-Type", "application/json")
	
	// Default response
	response := Response{
		Message:   "Hello from Middleware Patterns Example!",
		RequestID: requestID,
		Timestamp: time.Now().Format(time.RFC3339),
	}
	
	// Add context data
	data := map[string]interface{}{
		"path":       r.URL.Path,
		"method":     r.Method,
		"remoteAddr": r.RemoteAddr,
		"userAgent":  r.UserAgent(),
		"authUser":   authUser,
	}
	
	if !startTime.IsZero() {
		data["requestDuration"] = time.Since(startTime).String()
	}
	
	response.Data = data
	
	// Handle POST requests
	if r.Method == "POST" {
		body, err := io.ReadAll(r.Body)
		if err != nil {
			log.Printf("Error reading request body: %v", err)
		} else if len(body) > 0 {
			var jsonData interface{}
			if err := json.Unmarshal(body, &jsonData); err == nil {
				data["requestBody"] = jsonData
			} else {
				data["requestBody"] = string(body)
			}
		}
	}
	
	// Route handling
	switch r.URL.Path {
	case "/health":
		response.Message = "Health check passed"
		response.Data = map[string]string{"status": "healthy"}
	case "/protected":
		response.Message = "Access granted to protected endpoint"
	case "/panic":
		// Demonstrate recovery middleware
		panic("intentional panic for testing recovery middleware")
	default:
		response.Message = "Middleware patterns demonstration"
	}
	
	// Encode and send response
	responseBytes, err := json.Marshal(response)
	if err != nil {
		log.Printf("Error encoding response: %v", err)
		http.Error(w, "Internal Server Error", http.StatusInternalServerError)
		return
	}
	
	w.Write(responseBytes)
}

// Handle is the main entry point following the Telnyx Edge Compute pattern
func Handle(w http.ResponseWriter, r *http.Request) {
	// Get configuration from environment
	authToken := getEnvOrDefault("AUTH_TOKEN", "demo-token")
	
	// Create base handler
	baseHandler := http.HandlerFunc(appHandler)
	
	// Apply middleware chain
	handler := ApplyMiddleware(
		baseHandler,
		Recovery(),    // Always apply first (outermost)
		Logger(),      // Request logging
		CORS(),        // CORS support
		Auth(authToken), // Authentication
	)
	
	// Serve the request
	handler.ServeHTTP(w, r)
}

// Helper function to get environment variable with default
func getEnvOrDefault(key, defaultValue string) string {
	if value := os.Getenv(key); strings.TrimSpace(value) != "" {
		return value
	}
	return defaultValue
}