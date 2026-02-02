/**
 * extractErrorMessage
 * 
 * Parses an error object (typically from Axios) and returns a user-friendly string.
 * Handles FastAPI/Pydantic validation errors (array of objects) and standard HTTP errors.
 * 
 * @param {any} error - The error object caught in try/catch
 * @param {string} fallback - A fallback message if no specific error is found
 * @returns {string} The formatted error message
 */
export const extractErrorMessage = (error, fallback = 'An unexpected error occurred.') => {
    if (!error) return fallback;

    // Network errors (no response from server)
    if (error.code === 'ERR_NETWORK') {
        return 'Network error: Unable to connect to the server. Please check your connection.';
    }

    // Axios response errors
    if (error.response?.data) {
        const data = error.response.data;

        // 1. "detail" is a simple string (Handled manual HTTPExceptions)
        if (typeof data.detail === 'string') {
            return data.detail;
        }

        // 2. "detail" is an array (Pydantic validation errors)
        if (Array.isArray(data.detail)) {
            // Extract the first error message, or join them
            // Example: [{"loc": ["body", "email"], "msg": "value is not a valid email", "type": "value_error.email"}]
            const firstError = data.detail[0];
            if (firstError?.msg) {
                // If it has a location, maybe prepend it? e.g. "Email: value is not a valid email"
                const field = firstError.loc ? firstError.loc[firstError.loc.length - 1] : 'Field';
                return `${field}: ${firstError.msg}`;
            }
        }

        // 3. Any other message property checking
        if (data.message) return data.message;
    }

    // Fallback to error message from JS Error object
    return error.message || fallback;
};
