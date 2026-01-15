import { Upload, Zap } from 'lucide-react';
import { FileUploadProps } from '@/types/security';

export default function FileUpload({
  fileName,
  onFileUpload,
  onAnalyzeCode,
  isAnalyzing,
  hasCode
}: FileUploadProps) {
  return (
    <div className="flex items-center gap-2">
      <input
        type="file"
        accept=".py"
        onChange={onFileUpload}
        className="hidden"
        id="file-upload"
      />

      <label
        htmlFor="file-upload"
        className="btn btn-secondary cursor-pointer"
      >
        <Upload className="w-4 h-4" />
        Upload
      </label>

      <button
        onClick={onAnalyzeCode}
        disabled={!hasCode || isAnalyzing}
        className="btn btn-brand disabled:opacity-50 disabled:cursor-not-allowed"
      >
        {isAnalyzing ? (
          <>
            <div className="w-4 h-4 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            Analyzing...
          </>
        ) : (
          <>
            <Zap className="w-4 h-4" />
            Run Analysis
          </>
        )}
      </button>
    </div>
  );
}