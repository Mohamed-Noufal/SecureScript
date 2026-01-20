'use client'

import { useState } from 'react';
import { useAuth, useUser } from '@clerk/nextjs';
import { AnalysisResponse, SecurityIssue } from '@/types/security';
import CodeInput from '@/components/CodeInput';
import AnalysisResults from '@/components/AnalysisResults';
// import { Button } from "@/components/ui/button"; // Unused import removed
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
      <div className="h-[calc(100vh-4rem)] flex items-center justify-center p-6 bg-white relative overflow-hidden">
        {/* Aurora Background Effects */}
        <div className="absolute inset-0 z-0 pointer-events-none">
          {/* Top Right - Soft Blue */}
          <div className="absolute -top-[10%] -right-[10%] w-[50%] h-[50%] rounded-full bg-blue-100 blur-[120px] opacity-60 animate-pulse" />

          {/* Bottom Left - Soft Purple */}
          <div className="absolute -bottom-[10%] -left-[10%] w-[50%] h-[50%] rounded-full bg-purple-100 blur-[120px] opacity-60 animate-pulse delay-1000" />

          {/* Center - Very Subtle Pink */}
          <div className="absolute top-[30%] left-[30%] w-[40%] h-[40%] rounded-full bg-pink-50 blur-[100px] opacity-40 mix-blend-multiply" />
        </div>

        <div className="w-full max-w-6xl grid grid-cols-1 md:grid-cols-2 gap-12 items-center relative z-10">

          {/* Left Column: Marketing / Value Prop */}
          <div className="space-y-8 animate-in fade-in slide-in-from-left-4 duration-700">
            <div className="space-y-4">
              <h1 className="text-5xl font-extrabold tracking-tight lg:text-6xl text-foreground">
                Cut Security Risks <span className="text-primary">Instantly.</span>
              </h1>
              <p className="text-xl text-muted-foreground leading-relaxed max-w-lg">
                Supercharge your code with AI-powered vulnerability detection. Fix security holes in seconds, not days.
              </p>
            </div>

            <div className="flex items-center gap-4 text-sm font-medium text-muted-foreground">
              <div className="flex -space-x-2">
                <div className="w-8 h-8 rounded-full bg-blue-500 border-2 border-background" />
                <div className="w-8 h-8 rounded-full bg-purple-500 border-2 border-background" />
                <div className="w-8 h-8 rounded-full bg-green-500 border-2 border-background" />
              </div>
              <span>Ready to secure your scripts? Let&apos;s find every vulnerability.</span>
            </div>
          </div>

          {/* Right Column: Authentication Box */}
          <div className="flex justify-center md:justify-end animate-in fade-in slide-in-from-right-4 duration-700 delay-200">
            <div className="w-full max-w-sm bg-card border rounded-2xl p-8 shadow-2xl">
              <div className="text-center mb-8">
                <div className="w-12 h-12 bg-primary/10 rounded-xl flex items-center justify-center mx-auto mb-4">
                  <ShieldAlert className="w-6 h-6 text-primary" />
                </div>
                <h2 className="text-2xl font-bold tracking-tight">Welcome Back to SecureScript</h2>
                <p className="text-sm text-muted-foreground mt-2">
                  Sign in to access your private security dashboard.
                </p>
              </div>

              <div className="space-y-4">
                {/* The Header component handles the actual SignIn button logic via Clerk Provider. 
                     We are directing them visually to the top right or just indicating action here.
                     Actually, with Clerk we can embed a SignIn component here if we installed @clerk/nextjs completely, 
                     but for now we'll stick to the "Gate" message but styled better.
                 */}
                <div className="p-4 bg-muted/50 rounded-lg border border-dashed border-border text-center">
                  <p className="text-sm font-medium">
                    Please use the <span className="text-primary font-bold">Sign In</span> button
                    <br />in the navigation bar to continue.
                  </p>
                </div>
              </div>

              <div className="mt-8 pt-6 border-t text-center text-xs text-muted-foreground">
                By continuing, you agree to SecureScript&apos;s <a href="#" className="underline hover:text-primary">Terms of Service</a>.
              </div>
            </div>
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
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
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

  const handleFixIssue = async (issues: SecurityIssue | SecurityIssue[]) => {
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