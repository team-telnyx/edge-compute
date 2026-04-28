package main

import (
	"log"
	"net/http"
)

// Import the function module (all examples use "module function")
import "function"

func main() {
	log.Printf("🚀 Starting local server on :8080")

	// Use the package name directly
	http.HandleFunc("/", function.Handle)

	log.Printf("✅ Server ready at http://localhost:8080")

	if err := http.ListenAndServe(":8080", nil); err != nil {
		log.Fatalf("❌ Server failed: %v", err)
	}
}
