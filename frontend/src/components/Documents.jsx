import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentsAPI } from '../lib/api';
import { Upload, FileText, Trash2, CheckCircle, XCircle, Loader } from 'lucide-react';

export default function Documents() {
    const [uploading, setUploading] = useState(false);
    const queryClient = useQueryClient();

    const { data: documents, isLoading } = useQuery({
        queryKey: ['documents'],
        queryFn: async () => {
            const response = await documentsAPI.list();
            return response.data;
        },
    });

    const deleteMutation = useMutation({
        mutationFn: documentsAPI.delete,
        onSuccess: () => {
            queryClient.invalidateQueries(['documents']);
        },
    });

    const handleFileUpload = async (e) => {
        const file = e.target.files[0];
        if (!file) return;

        setUploading(true);
        const formData = new FormData();
        formData.append('file', file);
        formData.append('document_type', 'other');
        formData.append('court_level', 'not_applicable');

        try {
            await documentsAPI.upload(formData);
            queryClient.invalidateQueries(['documents']);
        } catch (error) {
            alert(error.response?.data?.detail || 'Upload failed');
        } finally {
            setUploading(false);
            e.target.value = '';
        }
    };

    return (
        <div className="h-screen flex flex-col">
            {/* Header */}
            <div className="bg-white border-b border-gray-200 px-6 py-4 flex items-center justify-between">
                <div>
                    <h2 className="text-xl font-bold text-gray-900">Document Library</h2>
                    <p className="text-sm text-gray-600">Upload and manage legal documents</p>
                </div>
                <label className="bg-primary-600 text-white px-4 py-2 rounded-lg font-medium hover:bg-primary-700 cursor-pointer flex items-center gap-2 transition">
                    <Upload className="w-5 h-5" />
                    Upload Document
                    <input
                        type="file"
                        onChange={handleFileUpload}
                        accept=".pdf,.docx,.txt"
                        className="hidden"
                        disabled={uploading}
                    />
                </label>
            </div>

            {/* Documents List */}
            <div className="flex-1 overflow-y-auto p-6">
                {isLoading && (
                    <div className="text-center py-12">
                        <Loader className="w-8 h-8 animate-spin text-primary-600 mx-auto" />
                        <p className="mt-4 text-gray-600">Loading documents...</p>
                    </div>
                )}

                {!isLoading && documents?.length === 0 && (
                    <div className="text-center py-12">
                        <FileText className="w-16 h-16 text-gray-400 mx-auto mb-4" />
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">No documents yet</h3>
                        <p className="text-gray-600">Upload your first legal document to get started</p>
                    </div>
                )}

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {documents?.map((doc) => (
                        <div key={doc.id} className="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                            <div className="flex items-start justify-between mb-3">
                                <div className="flex items-center gap-3">
                                    <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
                                        <FileText className="w-5 h-5 text-primary-600" />
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-medium text-gray-900 truncate">{doc.title || doc.filename}</h3>
                                        <p className="text-xs text-gray-500">{(doc.file_size_bytes / 1024).toFixed(1)} KB</p>
                                    </div>
                                </div>
                                <button
                                    onClick={() => deleteMutation.mutate(doc.id)}
                                    className="text-red-600 hover:text-red-700 p-1"
                                    disabled={deleteMutation.isPending}
                                >
                                    <Trash2 className="w-4 h-4" />
                                </button>
                            </div>

                            <div className="space-y-2 text-sm">
                                {doc.jurisdiction && (
                                    <div className="flex items-center gap-2">
                                        <span className="text-gray-500">Jurisdiction:</span>
                                        <span className="font-medium text-gray-900">{doc.jurisdiction}</span>
                                    </div>
                                )}
                                {doc.year && (
                                    <div className="flex items-center gap-2">
                                        <span className="text-gray-500">Year:</span>
                                        <span className="font-medium text-gray-900">{doc.year}</span>
                                    </div>
                                )}
                                <div className="flex items-center gap-2">
                                    <span className="text-gray-500">Status:</span>
                                    {doc.processed ? (
                                        <span className="flex items-center gap-1 text-green-600">
                                            <CheckCircle className="w-4 h-4" />
                                            Processed ({doc.chunk_count} chunks)
                                        </span>
                                    ) : (
                                        <span className="flex items-center gap-1 text-yellow-600">
                                            <Loader className="w-4 h-4 animate-spin" />
                                            Processing...
                                        </span>
                                    )}
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}
