import { useState, useEffect, useRef } from 'react';
import { useMutation } from '@tanstack/react-query';
import { chatAPI } from '../lib/api';
import { Send, AlertCircle, CheckCircle, Info } from 'lucide-react';

export default function Chat() {
    const [query, setQuery] = useState('');
    const [messages, setMessages] = useState(() => {
        const saved = localStorage.getItem('chat_history');
        return saved ? JSON.parse(saved) : [];
    });

    // Auto-scroll to bottom
    const messagesEndRef = useRef(null);
    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        localStorage.setItem('chat_history', JSON.stringify(messages));
        scrollToBottom();
    }, [messages]);

    const chatMutation = useMutation({
        mutationFn: chatAPI.query,
        onSuccess: (response) => {
            const data = response.data;
            // Use functional updates to avoid stale closure
            setMessages((prevMessages) => [
                ...prevMessages,
                { role: 'user', content: query },
                {
                    role: 'assistant',
                    content: data.response,
                    citations: data.citations,
                    confidence: data.confidence_score,
                    safety: data.safety_check,
                    agents: data.agents_used
                },
            ]);
            // Clear input after successful submission
            setQuery('');
        },
        onError: (error) => {
            // User-friendly error messages
            let errorMessage = 'We encountered an issue processing your request. Please try again.';

            if (error.response?.status === 401) {
                errorMessage = 'Your session has expired. Please log in again.';
            } else if (error.response?.status === 429) {
                errorMessage = 'Too many requests. Please wait a moment before trying again.';
            } else if (error.response?.status >= 500) {
                errorMessage = 'Our service is temporarily unavailable. Please try again in a few moments.';
            } else if (error.response?.data?.detail) {
                // Only show backend error if it's user-friendly
                const detail = error.response.data.detail;
                if (!detail.includes('Internal Server Error') && !detail.includes('RetryError')) {
                    errorMessage = detail;
                }
            }

            setMessages((prevMessages) => [
                ...prevMessages,
                { role: 'user', content: query },
                { role: 'error', content: errorMessage },
            ]);
            // Clear input even on error
            setQuery('');
        },
    });

    const handleSubmit = (e) => {
        e.preventDefault();
        if (!query.trim()) return;
        chatMutation.mutate({ query, include_citations: true });
    };

    return (
        <div className="h-screen flex flex-col">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4">
                <h2 className="text-xl font-bold text-gray-900">Legal AI Assistant</h2>
                <p className="text-sm text-gray-600">Ask legal questions and get AI-powered answers with citations</p>
            </div>

            {/* Messages */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
                {messages.length === 0 && (
                    <div className="text-center py-12">
                        <div className="inline-flex items-center justify-center w-16 h-16 bg-primary-100 rounded-full mb-4">
                            <Info className="w-8 h-8 text-primary-600" />
                        </div>
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">Welcome to Legal AI Assistant</h3>
                        <p className="text-gray-600 max-w-md mx-auto">
                            Ask questions about statutes, case law, contracts, or compliance. The AI will provide answers with proper citations.
                        </p>
                        <div className="mt-6 p-4 bg-yellow-50 border border-yellow-200 rounded-lg max-w-2xl mx-auto">
                            <p className="text-sm text-yellow-800">
                                <strong>Disclaimer:</strong> This platform provides general legal information and not legal advice.
                                Consult a qualified attorney for specific legal matters.
                            </p>
                        </div>
                    </div>
                )}

                {messages.map((message, index) => (
                    <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                        <div className={`max-w-3xl ${message.role === 'user' ? 'bg-primary-600 text-white' : message.role === 'error' ? 'bg-red-50 border border-red-200' : 'bg-white border border-gray-200'} rounded-lg p-4 shadow-sm`}>
                            {message.role === 'assistant' && (
                                <div className="mb-3 flex items-center gap-2 text-xs text-gray-500">
                                    <CheckCircle className="w-4 h-4" />
                                    <span>Confidence: {(message.confidence * 100).toFixed(0)}%</span>
                                    <span className="mx-2">•</span>
                                    <span>Agents: {message.agents?.join(', ')}</span>
                                </div>
                            )}

                            <div className={`whitespace-pre-wrap ${message.role === 'error' ? 'text-red-800' : message.role === 'user' ? 'text-white' : 'text-gray-900'}`}>
                                {message.content}
                            </div>

                            {message.citations && message.citations.length > 0 && (
                                <div className="mt-4 pt-4 border-t border-gray-200">
                                    <p className="text-sm font-semibold text-gray-700 mb-2">Citations:</p>
                                    <div className="space-y-2">
                                        {message.citations.map((citation, idx) => (
                                            <div key={idx} className="text-sm bg-gray-50 p-2 rounded">
                                                <p className="font-medium text-gray-900">{citation.source}</p>
                                                <p className="text-gray-600 text-xs mt-1">{citation.text}</p>
                                            </div>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </div>
                    </div>
                ))}

                {chatMutation.isPending && (
                    <div className="flex justify-start">
                        <div className="bg-white border border-gray-200 rounded-lg p-4 shadow-sm">
                            <div className="flex items-center gap-2">
                                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary-600"></div>
                                <span className="text-gray-600">AI is thinking...</span>
                            </div>
                        </div>
                    </div>
                )}
                <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div className="bg-white border-t border-gray-200 p-6">
                <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
                    <div className="flex gap-4">
                        <input
                            type="text"
                            value={query}
                            onChange={(e) => setQuery(e.target.value)}
                            placeholder="Ask a legal question..."
                            className="flex-1 px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent outline-none"
                            disabled={chatMutation.isPending}
                        />
                        <button
                            type="submit"
                            disabled={chatMutation.isPending || !query.trim()}
                            className="bg-primary-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-primary-700 focus:ring-4 focus:ring-primary-200 transition disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
                        >
                            <Send className="w-5 h-5" />
                            Send
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
