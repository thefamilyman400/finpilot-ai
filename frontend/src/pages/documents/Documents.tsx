import { useState, useRef } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { documentService } from '../../services/document.service';
import type { Document } from '../../types';
import MainLayout from '../../components/layout/MainLayout';

export default function Documents() {
  const queryClient = useQueryClient();
  const fileInputRef = useRef<HTMLInputElement>(null);
  const parseFileInputRef = useRef<HTMLInputElement>(null);
  
  const [selectedDocument, setSelectedDocument] = useState<Document | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [parseResult, setParseResult] = useState<any>(null);
  const [showParseResult, setShowParseResult] = useState(false);

  // Fetch documents
  const { data: documents, isLoading } = useQuery({
    queryKey: ['documents'],
    queryFn: () => documentService.getDocuments({}),
  });

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: ({ file, type }: { file: File; type: string }) =>
      documentService.uploadDocument(file, type),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    },
  });

  // Parse document mutation
  const parseMutation = useMutation({
    mutationFn: documentService.parseDocument,
    onSuccess: (data) => {
      setParseResult(data);
      setShowParseResult(true);
      queryClient.invalidateQueries({ queryKey: ['accounts'] });
      queryClient.invalidateQueries({ queryKey: ['transactions'] });
      if (parseFileInputRef.current) {
        parseFileInputRef.current.value = '';
      }
    },
    onError: (error: any) => {
      alert(`Parse failed: ${error.response?.data?.detail || error.message}`);
    },
  });

  // Delete mutation
  const deleteMutation = useMutation({
    mutationFn: documentService.deleteDocument,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['documents'] });
      setSelectedDocument(null);
    },
  });

  const handleParseFile = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    const file = files[0];
    parseMutation.mutate(file);
  };

  const handleFileSelect = (files: FileList | null) => {
    if (!files || files.length === 0) return;
    
    const file = files[0];
    const type = detectDocumentType(file.name);
    uploadMutation.mutate({ file, type });
  };

  const detectDocumentType = (filename: string): string => {
    const lower = filename.toLowerCase();
    if (lower.includes('tax') || lower.includes('1040') || lower.includes('w2')) return 'tax_form';
    if (lower.includes('statement') || lower.includes('bank')) return 'bank_statement';
    if (lower.includes('invoice')) return 'invoice';
    if (lower.includes('receipt')) return 'receipt';
    if (lower.includes('pay') || lower.includes('payslip')) return 'payslip';
    return 'other';
  };

  const handleDragOver = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(true);
  };

  const handleDragLeave = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
  };

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    handleFileSelect(e.dataTransfer.files);
  };

  const formatFileSize = (bytes: number) => {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
  };

  const formatDate = (dateString: string) => {
    return new Date(dateString).toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  };

  const getDocumentIcon = (type: string) => {
    const icons: Record<string, string> = {
      tax_form: '📋',
      bank_statement: '🏦',
      invoice: '📄',
      receipt: '🧾',
      payslip: '💰',
      other: '📁',
    };
    return icons[type] || '📄';
  };

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      pending: 'rgb(251 191 36)',
      processing: 'rgb(59 130 246)',
      completed: 'rgb(34 197 94)',
      failed: 'rgb(239 68 68)',
    };
    return colors[status] || 'rgb(107 114 128)';
  };

  return (
    <MainLayout>
      <div style={{ marginBottom: '2rem' }}>
        <h2 style={{ fontSize: '2rem', fontWeight: 'bold', color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
          📄 Document Intelligence
        </h2>
          <p style={{ color: 'rgb(107 114 128)' }}>
            Upload financial documents for AI-powered analysis and data extraction
          </p>
        </div>

        {/* Parse & Import Section */}
        <div className="card" style={{ marginBottom: '2rem', backgroundColor: 'rgb(239 246 255)', border: '2px solid rgb(59 130 246)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '1rem' }}>
            <span style={{ fontSize: '2rem' }}>🔍</span>
            <div style={{ flex: 1 }}>
              <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'rgb(17 24 39)', marginBottom: '0.25rem' }}>
                Parse & Import Bank Statements
              </h3>
              <p style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)' }}>
                Automatically extract transactions and create accounts from your bank statements
              </p>
            </div>
          </div>
          <input
            ref={parseFileInputRef}
            type="file"
            accept=".pdf,.txt"
            onChange={(e) => handleParseFile(e.target.files)}
            style={{ display: 'none' }}
          />
          <button
            onClick={() => parseFileInputRef.current?.click()}
            className="btn-primary"
            disabled={parseMutation.isPending}
            style={{ width: '100%' }}
          >
            {parseMutation.isPending ? '🔄 Parsing...' : '📤 Upload & Parse Statement'}
          </button>
          <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginTop: '0.5rem', textAlign: 'center' }}>
            Supports: PDF & TXT bank statements from HDFC, ICICI, SBI, AXIS, KOTAK, and more
          </p>
        </div>

        {/* Upload Area */}
        <div
          className="card"
          style={{
            marginBottom: '2rem',
            border: isDragging ? '2px dashed rgb(59 130 246)' : '2px dashed rgb(229 231 235)',
            backgroundColor: isDragging ? 'rgb(239 246 255)' : 'white',
            transition: 'all 0.2s',
          }}
          onDragOver={handleDragOver}
          onDragLeave={handleDragLeave}
          onDrop={handleDrop}
        >
          <div style={{ textAlign: 'center', padding: '2rem' }}>
            <div style={{ fontSize: '3rem', marginBottom: '1rem' }}>📤</div>
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
              Upload Documents
            </h3>
            <p style={{ color: 'rgb(107 114 128)', marginBottom: '1.5rem' }}>
              Drag and drop files here, or click to browse
            </p>
            <input
              ref={fileInputRef}
              type="file"
              accept=".pdf,.txt,.jpg,.jpeg,.png,.doc,.docx"
              onChange={(e) => handleFileSelect(e.target.files)}
              style={{ display: 'none' }}
            />
            <button
              onClick={() => fileInputRef.current?.click()}
              className="btn-primary"
              disabled={uploadMutation.isPending}
            >
              {uploadMutation.isPending ? 'Uploading...' : 'Choose File'}
            </button>
            <p style={{ fontSize: '0.75rem', color: 'rgb(156 163 175)', marginTop: '1rem' }}>
              Supported formats: PDF, TXT, JPG, PNG, DOC, DOCX (Max 10MB)
            </p>
          </div>
        </div>

        <div style={{ display: 'grid', gridTemplateColumns: selectedDocument ? '1fr 1fr' : '1fr', gap: '2rem' }}>
          {/* Documents List */}
          <div className="card">
            <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'rgb(17 24 39)', marginBottom: '1.5rem' }}>
              Your Documents ({documents?.length || 0})
            </h3>

            {isLoading ? (
              <div style={{ textAlign: 'center', padding: '3rem', color: 'rgb(107 114 128)' }}>
                Loading documents...
              </div>
            ) : documents && documents.length > 0 ? (
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {documents.map((doc) => (
                  <div
                    key={doc.id}
                    onClick={() => setSelectedDocument(doc)}
                    style={{
                      padding: '1rem',
                      border: selectedDocument?.id === doc.id ? '2px solid rgb(59 130 246)' : '1px solid rgb(229 231 235)',
                      borderRadius: '0.5rem',
                      cursor: 'pointer',
                      transition: 'all 0.2s',
                      backgroundColor: selectedDocument?.id === doc.id ? 'rgb(239 246 255)' : 'white',
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start' }}>
                      <div style={{ flex: 1 }}>
                        <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', marginBottom: '0.5rem' }}>
                          <span style={{ fontSize: '1.5rem' }}>{getDocumentIcon(doc.document_type)}</span>
                          <h4 style={{ fontSize: '0.875rem', fontWeight: '600', color: 'rgb(17 24 39)' }}>
                            {doc.filename}
                          </h4>
                        </div>
                        <div style={{ display: 'flex', gap: '1rem', fontSize: '0.75rem', color: 'rgb(107 114 128)' }}>
                          <span>{formatFileSize(doc.file_size)}</span>
                          <span>•</span>
                          <span>{formatDate(doc.created_at)}</span>
                        </div>
                      </div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                        <span
                          style={{
                            padding: '0.25rem 0.5rem',
                            borderRadius: '0.25rem',
                            fontSize: '0.75rem',
                            fontWeight: '500',
                            backgroundColor: `${getStatusColor(doc.status)}20`,
                            color: getStatusColor(doc.status),
                          }}
                        >
                          {doc.status}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div style={{ textAlign: 'center', padding: '3rem' }}>
                <p style={{ color: 'rgb(107 114 128)', marginBottom: '1rem' }}>
                  No documents uploaded yet
                </p>
                <p style={{ color: 'rgb(156 163 175)', fontSize: '0.875rem' }}>
                  Upload your first document to get started with AI analysis
                </p>
              </div>
            )}
          </div>

          {/* Document Details */}
          {selectedDocument && (
            <div className="card">
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.125rem', fontWeight: '600', color: 'rgb(17 24 39)' }}>
                  Document Details
                </h3>
                <button
                  onClick={() => {
                    if (window.confirm('Are you sure you want to delete this document?')) {
                      deleteMutation.mutate(selectedDocument.id);
                    }
                  }}
                  style={{
                    padding: '0.5rem 1rem',
                    backgroundColor: 'rgb(254 242 242)',
                    color: 'rgb(153 27 27)',
                    border: '1px solid rgb(252 165 165)',
                    borderRadius: '0.5rem',
                    fontSize: '0.875rem',
                    fontWeight: '500',
                    cursor: 'pointer',
                  }}
                >
                  Delete
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1rem' }}>
                <div>
                  <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginBottom: '0.25rem' }}>Filename</p>
                  <p style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(17 24 39)' }}>{selectedDocument.filename}</p>
                </div>

                <div>
                  <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginBottom: '0.25rem' }}>Type</p>
                  <p style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(17 24 39)', textTransform: 'capitalize' }}>
                    {selectedDocument.document_type.replace(/_/g, ' ')}
                  </p>
                </div>

                <div>
                  <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginBottom: '0.25rem' }}>Size</p>
                  <p style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(17 24 39)' }}>
                    {formatFileSize(selectedDocument.file_size)}
                  </p>
                </div>

                <div>
                  <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginBottom: '0.25rem' }}>Status</p>
                  <span
                    style={{
                      display: 'inline-block',
                      padding: '0.25rem 0.75rem',
                      borderRadius: '0.25rem',
                      fontSize: '0.875rem',
                      fontWeight: '500',
                      backgroundColor: `${getStatusColor(selectedDocument.status)}20`,
                      color: getStatusColor(selectedDocument.status),
                      textTransform: 'capitalize',
                    }}
                  >
                    {selectedDocument.status}
                  </span>
                </div>

                {selectedDocument.extracted_text && (
                  <div>
                    <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>Extracted Text</p>
                    <div
                      style={{
                        padding: '1rem',
                        backgroundColor: 'rgb(249 250 251)',
                        borderRadius: '0.5rem',
                        maxHeight: '200px',
                        overflowY: 'auto',
                        fontSize: '0.875rem',
                        color: 'rgb(55 65 81)',
                        lineHeight: '1.5',
                      }}
                    >
                      {selectedDocument.extracted_text}
                    </div>
                  </div>
                )}

                {selectedDocument.ai_analysis && (
                  <div>
                    <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>AI Analysis</p>
                    <div
                      style={{
                        padding: '1rem',
                        backgroundColor: 'rgb(240 253 244)',
                        border: '1px solid rgb(187 247 208)',
                        borderRadius: '0.5rem',
                        fontSize: '0.875rem',
                        color: 'rgb(21 128 61)',
                        lineHeight: '1.5',
                      }}
                    >
                      {typeof selectedDocument.ai_analysis === 'string' 
                        ? selectedDocument.ai_analysis 
                        : JSON.stringify(selectedDocument.ai_analysis, null, 2)}
                    </div>
                  </div>
                )}

                {selectedDocument.extracted_data && Object.keys(selectedDocument.extracted_data).length > 0 && (
                  <div>
                    <p style={{ fontSize: '0.75rem', color: 'rgb(107 114 128)', marginBottom: '0.5rem' }}>Extracted Data</p>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
                      {Object.entries(selectedDocument.extracted_data).map(([key, value]) => (
                        <div
                          key={key}
                          style={{
                            display: 'flex',
                            justifyContent: 'space-between',
                            padding: '0.75rem',
                            backgroundColor: 'rgb(249 250 251)',
                            borderRadius: '0.375rem',
                          }}
                        >
                          <span style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)', textTransform: 'capitalize' }}>
                            {key.replace(/_/g, ' ')}:
                          </span>
                          <span style={{ fontSize: '0.875rem', fontWeight: '500', color: 'rgb(17 24 39)' }}>
                            {String(value)}
                          </span>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}
        </div>

        {/* Parse Result Modal */}
        {showParseResult && parseResult && (
          <div
            style={{
              position: 'fixed',
              top: 0,
              left: 0,
              right: 0,
              bottom: 0,
              backgroundColor: 'rgba(0, 0, 0, 0.5)',
              display: 'flex',
              alignItems: 'center',
              justifyContent: 'center',
              zIndex: 1000,
            }}
            onClick={() => setShowParseResult(false)}
          >
            <div
              className="card"
              style={{
                maxWidth: '600px',
                width: '90%',
                maxHeight: '80vh',
                overflowY: 'auto',
              }}
              onClick={(e) => e.stopPropagation()}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'start', marginBottom: '1.5rem' }}>
                <h3 style={{ fontSize: '1.5rem', fontWeight: '600', color: 'rgb(17 24 39)' }}>
                  ✅ Parse Complete!
                </h3>
                <button
                  onClick={() => setShowParseResult(false)}
                  style={{
                    padding: '0.5rem',
                    backgroundColor: 'transparent',
                    border: 'none',
                    fontSize: '1.5rem',
                    cursor: 'pointer',
                    color: 'rgb(107 114 128)',
                  }}
                >
                  ×
                </button>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
                {/* Summary Stats */}
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '1rem' }}>
                  <div style={{ padding: '1rem', backgroundColor: 'rgb(240 253 244)', borderRadius: '0.5rem', border: '1px solid rgb(187 247 208)' }}>
                    <p style={{ fontSize: '0.75rem', color: 'rgb(21 128 61)', marginBottom: '0.25rem' }}>Transactions Found</p>
                    <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'rgb(21 128 61)' }}>{parseResult.transactions_found}</p>
                  </div>
                  <div style={{ padding: '1rem', backgroundColor: 'rgb(239 246 255)', borderRadius: '0.5rem', border: '1px solid rgb(191 219 254)' }}>
                    <p style={{ fontSize: '0.75rem', color: 'rgb(29 78 216)', marginBottom: '0.25rem' }}>Transactions Imported</p>
                    <p style={{ fontSize: '1.5rem', fontWeight: 'bold', color: 'rgb(29 78 216)' }}>{parseResult.transactions_created}</p>
                  </div>
                </div>

                {/* Bank Details */}
                {parseResult.detected_bank && (
                  <div style={{ padding: '1rem', backgroundColor: 'rgb(249 250 251)', borderRadius: '0.5rem' }}>
                    <p style={{ fontSize: '0.875rem', fontWeight: '600', color: 'rgb(17 24 39)', marginBottom: '0.5rem' }}>
                      🏦 Bank Detected
                    </p>
                    <p style={{ fontSize: '1rem', color: 'rgb(55 65 81)' }}>{parseResult.detected_bank}</p>
                    {parseResult.account_number && (
                      <p style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)', marginTop: '0.25rem' }}>
                        Account: ****{parseResult.account_number}
                      </p>
                    )}
                    {parseResult.detected_account_type && (
                      <p style={{ fontSize: '0.875rem', color: 'rgb(107 114 128)' }}>
                        Type: {parseResult.detected_account_type.replace(/_/g, ' ').toUpperCase()}
                      </p>
                    )}
                  </div>
                )}

                {/* Accounts Created */}
                {parseResult.accounts_created > 0 && (
                  <div style={{ padding: '1rem', backgroundColor: 'rgb(254 249 195)', borderRadius: '0.5rem', border: '1px solid rgb(253 224 71)' }}>
                    <p style={{ fontSize: '0.875rem', fontWeight: '600', color: 'rgb(113 63 18)' }}>
                      ✨ {parseResult.accounts_created} New Account Created
                    </p>
                  </div>
                )}

                {/* Errors */}
                {parseResult.errors && parseResult.errors.length > 0 && (
                  <div style={{ padding: '1rem', backgroundColor: 'rgb(254 242 242)', borderRadius: '0.5rem', border: '1px solid rgb(252 165 165)' }}>
                    <p style={{ fontSize: '0.875rem', fontWeight: '600', color: 'rgb(153 27 27)', marginBottom: '0.5rem' }}>
                      ⚠️ Errors
                    </p>
                    <ul style={{ margin: 0, paddingLeft: '1.5rem', color: 'rgb(153 27 27)', fontSize: '0.875rem' }}>
                      {parseResult.errors.map((error: string, index: number) => (
                        <li key={index}>{error}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Warnings */}
                {parseResult.warnings && parseResult.warnings.length > 0 && (
                  <div style={{ padding: '1rem', backgroundColor: 'rgb(254 252 232)', borderRadius: '0.5rem', border: '1px solid rgb(253 224 71)' }}>
                    <p style={{ fontSize: '0.875rem', fontWeight: '600', color: 'rgb(113 63 18)', marginBottom: '0.5rem' }}>
                      ℹ️ Warnings
                    </p>
                    <ul style={{ margin: 0, paddingLeft: '1.5rem', color: 'rgb(113 63 18)', fontSize: '0.875rem' }}>
                      {parseResult.warnings.map((warning: string, index: number) => (
                        <li key={index}>{warning}</li>
                      ))}
                    </ul>
                  </div>
                )}

                {/* Success Message */}
                <div style={{ padding: '1rem', backgroundColor: 'rgb(240 253 244)', borderRadius: '0.5rem', textAlign: 'center' }}>
                  <p style={{ fontSize: '0.875rem', color: 'rgb(21 128 61)' }}>
                    🎉 Your transactions have been imported! Check the Accounts and Transactions pages to view them.
                  </p>
                </div>

                {/* Close Button */}
                <button
                  onClick={() => setShowParseResult(false)}
                  className="btn-primary"
                  style={{ width: '100%' }}
                >
                  Close
                </button>
              </div>
            </div>
          </div>
        )}
    </MainLayout>
  );
}

// Made with Bob