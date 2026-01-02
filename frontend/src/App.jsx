import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Upload, File, Sparkles, Check, Copy, Clock } from 'lucide-react';
import axios from 'axios';

function App() {
    const [dragActive, setDragActive] = useState(false);
    const [files, setFiles] = useState([]);
    const [uploading, setUploading] = useState(false);
    const [expiration, setExpiration] = useState('never');
    const [result, setResult] = useState(null);

    const handleDrag = (e) => {
        e.preventDefault();
        e.stopPropagation();
        if (e.type === "dragenter" || e.type === "dragover") {
            setDragActive(true);
        } else if (e.type === "dragleave") {
            setDragActive(false);
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        e.stopPropagation();
        setDragActive(false);
        if (e.dataTransfer.files && e.dataTransfer.files[0]) {
            setFiles(Array.from(e.dataTransfer.files));
        }
    };

    const handleChange = (e) => {
        e.preventDefault();
        if (e.target.files && e.target.files[0]) {
            setFiles(Array.from(e.target.files));
        }
    };

    const handleUpload = async () => {
        if (files.length === 0) return;
        setUploading(true);

        const formData = new FormData();
        files.forEach(file => {
            formData.append('files', file);
        });
        formData.append('expiration', expiration);

        try {
            const baseURL = import.meta.env.DEV ? 'http://127.0.0.1:8000' : '';
            const response = await axios.post(`${baseURL}/upload`, formData);
            setResult(response.data);
            setFiles([]);
        } catch (error) {
            console.error(error);
            alert('Upload failed');
        } finally {
            setUploading(false);
        }
    };

    const copyToClipboard = () => {
        if (result) {
            let link = result.download_url;
            if (import.meta.env.DEV) {
                link = `http://127.0.0.1:8000${result.download_url}`;
            } else {
                link = `${window.location.origin}${result.download_url}`;
            }
            navigator.clipboard.writeText(link);
            alert("Copied!");
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-indigo-500 via-purple-500 to-pink-500 flex items-center justify-center p-4">
            <AnimatePresence>
                {!result ? (
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        exit={{ opacity: 0, y: -20 }}
                        className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 w-full max-w-md shadow-2xl border border-white/20"
                    >
                        <div className="text-center mb-8">
                            <h1 className="text-3xl font-bold text-white mb-2 flex items-center justify-center gap-2">
                                <Sparkles className="w-8 h-8 text-yellow-300" />
                                ArtyrkUpload
                            </h1>
                            <p className="text-white/70">Upload files securely & fast</p>
                        </div>

                        <div
                            className={`relative border-2 border-dashed rounded-2xl p-10 text-center transition-all duration-300 ${dragActive ? 'border-white bg-white/10' : 'border-white/30 hover:border-white/50'
                                }`}
                            onDragEnter={handleDrag}
                            onDragLeave={handleDrag}
                            onDragOver={handleDrag}
                            onDrop={handleDrop}
                        >
                            <input
                                type="file"
                                multiple
                                className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
                                onChange={handleChange}
                            />

                            {files.length > 0 ? (
                                <div className="flex flex-col items-center">
                                    <File className="w-12 h-12 text-white mb-2" />
                                    <p className="text-white font-medium">{files.length} file(s) selected</p>
                                    <p className="text-white/50 text-sm mt-1">Click to change</p>
                                </div>
                            ) : (
                                <div className="flex flex-col items-center">
                                    <Upload className="w-12 h-12 text-white mb-2" />
                                    <p className="text-white font-medium">Drag & Drop files here</p>
                                    <p className="text-white/50 text-sm mt-1">or click to browse</p>
                                </div>
                            )}
                        </div>

                        <div className="mt-6 space-y-4">
                            <div>
                                <label className="text-white/80 text-sm block mb-2 flex items-center gap-2">
                                    <Clock className="w-4 h-4" /> Expiration
                                </label>
                                <select
                                    value={expiration}
                                    onChange={(e) => setExpiration(e.target.value)}
                                    className="w-full bg-white/10 border border-white/20 rounded-xl px-4 py-2 text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-white/50 [&>option]:text-black"
                                >
                                    <option value="never">Never</option>
                                    <option value="1d">1 Day</option>
                                    <option value="7d">7 Days</option>
                                    <option value="1m">1 Month</option>
                                </select>
                            </div>

                            <button
                                onClick={handleUpload}
                                disabled={uploading || files.length === 0}
                                className="w-full bg-white text-purple-600 font-bold py-3 rounded-xl hover:bg-white/90 transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
                            >
                                {uploading ? (
                                    <>Uploading...</>
                                ) : (
                                    <>Upload Now</>
                                )}
                            </button>
                        </div>
                    </motion.div>
                ) : (
                    <motion.div
                        initial={{ opacity: 0, scale: 0.9 }}
                        animate={{ opacity: 1, scale: 1 }}
                        className="bg-white/10 backdrop-blur-lg rounded-3xl p-8 w-full max-w-md shadow-2xl border border-white/20 text-center"
                    >
                        <div className="w-16 h-16 bg-green-400 rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg">
                            <Check className="w-8 h-8 text-white" />
                        </div>
                        <h2 className="text-3xl font-bold text-white mb-2">Success!</h2>
                        <p className="text-white/70 mb-8">Your files are ready to share</p>

                        <div className="bg-white/5 rounded-xl p-4 mb-6 break-all">
                            <p className="text-white/90 font-mono text-sm">
                                {import.meta.env.DEV ? `http://127.0.0.1:8000${result.download_url}` : `${window.location.origin}${result.download_url}`}
                            </p>
                        </div>

                        <div className="grid grid-cols-2 gap-4">
                            <button
                                onClick={copyToClipboard}
                                className="bg-white text-purple-600 font-bold py-3 rounded-xl hover:bg-white/90 transition-colors flex items-center justify-center gap-2"
                            >
                                <Copy className="w-5 h-5" /> Copy Link
                            </button>
                            <button
                                onClick={() => { setResult(null); setFiles([]); }}
                                className="bg-white/20 text-white font-bold py-3 rounded-xl hover:bg-white/30 transition-colors"
                            >
                                Upload More
                            </button>
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </div>
    );
}

export default App;
