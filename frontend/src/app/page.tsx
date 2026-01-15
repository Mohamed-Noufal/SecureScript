'use client'

import { useState } from 'react';
import { useAuth, useUser } from '@clerk/nextjs';
import { AnalysisResponse } from '@/types/security';
import CodeInput from '@/components/CodeInput';
import AnalysisResults from '@/components/AnalysisResults';
import { Button } from "@/components/ui/button";
import { ShieldAlert } from "lucide-react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function Home() {
  const [codeContent, setCodeContent] = useState('');
  const [fileName, setFileName] = useState('');
  const [analysisResults, setAnalysisResults] = useState<AnalysisResponse | null>(null);
  const [isAnalyzing, setIsAnalyzing] = useState(false);
  const [isFixing, setIsFixing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const { getToken, isSignedIn, isLoaded } = useAuth();
  const { user } = useUser();

  if (!isLoaded) {
    return <div className="h-screen flex items-center justify-center">Loading...</div>;
  }

  if (!isSignedIn) {
    return (
      <div className="h-[calc(100vh-4rem)] flex items-center justify-center p-6">
        <div className="max-w-md w-full bg-card border rounded-xl p-8 text-center shadow-lg">
          <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-6">
            <ShieldAlert className="w-8 h-8 text-primary" />
          </div>
          <h1 className="text-2xl font-bold mb-2">Authentication Required</h1>
          <p className="text-muted-foreground mb-6">
            You must be signed in to use SecureScript. Access is restricted to authorized security personnel.
          </p>
          <div className="flex justify-center">
            {/* The Header component handles the actual SignIn button logic via Clerk Proivder */}
            <p className="text-sm font-medium text-primary">Please use the "Sign In" button in the top right.</p>
          </div>
        </div>
      </div>
    );
  }

  const handleFileUpload = (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (file && file.name.endsWith('.py')) {
      setFileName(file.name);
      const reader = new FileReader();
      reader.onload = (e) => {
        const content = e.target?.result as string;
        setCodeContent(content);
        (window as any).originalCode = content;
        setAnalysisResults(null);
        setError(null);
      };
      reader.readAsText(file);
    }
  };

  const handleAnalyzeCode = async () => {
    if (!codeContent) return;
    setIsAnalyzing(true);
    setError(null);

    try {
      const token = await getToken();
      const userEmail = user?.primaryEmailAddress?.emailAddress;

      const response = await fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Email': userEmail || '',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: JSON.stringify({ code: codeContent }),
      });

      if (response.status === 429) {
        throw new Error("Daily limit reached (7 requests/day). Come back tomorrow!");
      }
      if (!response.ok) throw new Error(`Failed: ${response.status}`);
      setAnalysisResults(await response.json());
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Error');
    } finally {
      setIsAnalyzing(false);
    }
  };


  // ... existing handlers ...

  const handleFixIssue = async (issues: any | any[]) => {
    if (!codeContent) return;
    setIsFixing(true);

    const issuesToFix = Array.isArray(issues) ? issues : [issues];

    // Optimistic UI: Scroll to top of editor or give visual feedback?
    // For now, we will clear the code and let it stream in "like typing"
    // But maybe we should wait for the first chunk to clear? 
    // Let's wait for 'start' event to clear.

    try {
      const token = await getToken();
      const userEmail = user?.primaryEmailAddress?.emailAddress;

      const response = await fetch(`${API_BASE_URL}/api/fix`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-User-Email': userEmail || '',
          ...(token && { 'Authorization': `Bearer ${token}` }),
        },
        body: JSON.stringify({
          code: codeContent,
          issues: issuesToFix
        }),
      });

      if (response.status === 429) {
        throw new Error("Daily limit reached (7 requests/day). Come back tomorrow!");
      }
      if (!response.ok) throw new Error(`Fix failed: ${response.status}`);
      if (!response.body) throw new Error("No response stream");

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        // Split by double newline to get events
        const events = buffer.split('\n\n');
        buffer = events.pop() || ''; // Keep the incomplete part

        for (const eventStr of events) {
          const lines = eventStr.split('\n');
          let eventType = '';
          let data = '';

          for (const line of lines) {
            if (line.startsWith('event: ')) eventType = line.slice(7).trim();
            if (line.startsWith('data: ')) data = line.slice(6).trim();
          }

          if (eventType === 'start') {
            // Clear code to prepare for streaming "typing" effect
            setCodeContent('');
          } else if (eventType === 'chunk') {
            try {
              const parsed = JSON.parse(data);
              if (parsed.chunk) {
                setCodeContent(prev => prev + parsed.chunk);
              }
            } catch (e) {
              console.error("Failed to parse chunk", e);
            }
          } else if (eventType === 'complete') {
            setIsFixing(false);
          } else if (eventType === 'error') {
            console.error("Fix stream error");
            setIsFixing(false);
          }
        }
      }
    } catch (err) {
      console.error("Fix error:", err);
      setError("Failed to apply fix");
      setIsFixing(false);
    }
  };

  return (
    <div className="h-[calc(100vh-4rem)] p-6 grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Code Editor Panel */}
      <div className="min-h-0">
        <CodeInput
          codeContent={codeContent}
          fileName={fileName}
          onFileUpload={handleFileUpload}
          onAnalyzeCode={handleAnalyzeCode}
          isAnalyzing={isAnalyzing || isFixing}
        />
      </div>

      {/* Analysis Results Panel */}
      <div className="min-h-0 overflow-hidden">
        <AnalysisResults
          analysisResults={analysisResults}
          isAnalyzing={isAnalyzing}
          error={error}
          onFix={handleFixIssue}
        />
      </div>
    </div>
  );
}