import { useState } from 'react';
import { Routes, Route, Link, useNavigate } from 'react-router-dom';
import { Scale, MessageSquare, FileText, LogOut, Upload } from 'lucide-react';
import Chat from '../components/Chat';
import Documents from '../components/Documents';

export default function Workspace({ setAuth }) {
    const navigate = useNavigate();

    const handleLogout = () => {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
        setAuth(false);
        navigate('/login');
    };

    return (
        <div className="min-h-screen bg-gray-50 flex">
            {/* Sidebar */}
            <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
                <div className="p-6 border-b border-gray-200">
                    <div className="flex items-center gap-3">
                        <div className="w-10 h-10 bg-primary-600 rounded-lg flex items-center justify-center">
                            <Scale className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h1 className="font-bold text-gray-900">Legal AI</h1>
                            <p className="text-xs text-gray-500">SaaS Platform</p>
                        </div>
                    </div>
                </div>

                <nav className="flex-1 p-4">
                    <Link
                        to="/workspace/chat"
                        className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 hover:text-gray-900 transition mb-2"
                    >
                        <MessageSquare className="w-5 h-5" />
                        <span className="font-medium">Legal Chat</span>
                    </Link>
                    <Link
                        to="/workspace/documents"
                        className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-gray-100 text-gray-700 hover:text-gray-900 transition"
                    >
                        <FileText className="w-5 h-5" />
                        <span className="font-medium">Documents</span>
                    </Link>
                </nav>

                <div className="p-4 border-t border-gray-200">
                    <button
                        onClick={handleLogout}
                        className="flex items-center gap-3 px-4 py-3 rounded-lg hover:bg-red-50 text-red-600 hover:text-red-700 transition w-full"
                    >
                        <LogOut className="w-5 h-5" />
                        <span className="font-medium">Logout</span>
                    </button>
                </div>
            </div>

            {/* Main Content */}
            <div className="flex-1">
                <Routes>
                    <Route path="/" element={<Chat />} />
                    <Route path="/chat" element={<Chat />} />
                    <Route path="/documents" element={<Documents />} />
                </Routes>
            </div>
        </div>
    );
}
