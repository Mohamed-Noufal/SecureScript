import { X, Save, Play, Check, Upload } from "lucide-react";
import { Button } from "@/components/ui/button";
import { CodeInputProps } from "@/types/security";

export default function CodeInput({
  codeContent,
  fileName,
  onFileUpload,
  onAnalyzeCode,
  isAnalyzing
}: CodeInputProps) {
  const lines = codeContent ? codeContent.split('\n') : [];

  return (
    <div className="flex flex-col h-full bg-card rounded-xl border shadow-card overflow-hidden">
      {/* Tab bar */}
      <div className="flex items-center justify-between px-4 py-2 border-b bg-muted/30">
        <div className="flex items-center gap-2">
          {fileName ? (
            <div className="flex items-center gap-2 px-3 py-1.5 bg-card rounded-md border">
              <div className="w-4 h-4 rounded bg-high/20 flex items-center justify-center">
                <span className="text-[10px]">🐍</span>
              </div>
              <span className="text-sm font-medium">{fileName}</span>
              <button className="p-0.5 hover:bg-muted rounded">
                <X className="w-3 h-3 text-muted-foreground" />
              </button>
            </div>
          ) : (
            <div className="text-sm text-muted-foreground italic px-2">No file open</div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <input
            type="file"
            accept=".py"
            onChange={onFileUpload}
            className="hidden"
            id="file-upload"
          />
          <Button variant="outline" size="sm" className="gap-1.5" asChild>
            <label htmlFor="file-upload" className="cursor-pointer">
              <Upload className="w-4 h-4" />
              Open
            </label>
          </Button>



          <Button
            size="sm"
            className="gap-1.5 bg-primary hover:bg-primary/90"
            onClick={onAnalyzeCode}
            disabled={!codeContent || isAnalyzing}
          >
            {isAnalyzing ? (
              <div className="w-4 h-4 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin" />
            ) : (
              <Play className="w-4 h-4" />
            )}
            Run Analysis
          </Button>

          <Button variant="outline" size="sm" className="gap-1.5">
            <Check className="w-4 h-4" />
            Commit
          </Button>
        </div>
      </div>

      {/* Code area */}
      <div className="flex-1 overflow-auto code-editor text-sm scrollbar-thin flex flex-col relative">
        {!codeContent ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center p-8">
            <div className="w-16 h-16 bg-muted rounded-full flex items-center justify-center mb-4">
              <Upload className="w-8 h-8 text-muted-foreground/50" />
            </div>
            <h3 className="text-lg font-semibold mb-2">Open a Python file</h3>
            <p className="text-muted-foreground mb-6 max-w-xs">
              Upload a .py file to start scanning for security vulnerabilities
            </p>
            <Button size="lg" asChild>
              <label htmlFor="file-upload" className="cursor-pointer">
                Browse Files
              </label>
            </Button>
          </div>
        ) : (

          <div className="p-4 min-w-max font-mono text-sm leading-6">
            {lines.map((line, i) => {
              const num = i + 1;
              const isHighlight = line.includes("api_key") || line.includes("secret") || line.includes("password");

              // Basic syntax highlighting helper
              const highlightSyntax = (text: string) => {
                const parts: React.ReactNode[] = [];
                let currentText = text;

                // 1. Comments
                const commentIdx = currentText.indexOf('#');
                let comment = '';
                if (commentIdx !== -1) {
                  comment = currentText.slice(commentIdx);
                  currentText = currentText.slice(0, commentIdx);
                }

                // 2. Split by common delimiters to finding tokens
                // This is a very simple tokenizer for visual effect
                const tokens = currentText.split(/(\s+|[(){}[\]=,.'"*])/);

                tokens.forEach((token, idx) => {
                  let className = "text-foreground"; // default variable color

                  if (['def', 'class', 'import', 'from', 'return', 'if', 'else', 'try', 'except', 'print', 'in', 'as'].includes(token)) {
                    className = "code-keyword font-semibold";
                  } else if (['True', 'False', 'None'].includes(token)) {
                    className = "code-keyword italic";
                  } else if (token.match(/^[0-9]+$/)) {
                    className = "text-[#098658]"; // Number color green
                  } else if (token.startsWith('"') || token.startsWith("'")) {
                    className = "code-string";
                  } else if (token.match(/^[A-Z][a-zA-Z0-9_]*$/) && token !== token.toUpperCase()) {
                    // PascalCase often classes in Python
                    className = "text-[#267f99]";
                  } else if (token.match(/^[a-z_][a-z0-9_]*$/) && i > 0 && lines[i].trim().startsWith('def ')) {
                    // Function definition name heuristic (imperfect but helps)
                    className = "code-function";
                  }

                  // Strings logic needs better handling (this splits quotes), so manual override for demo:
                  if (token.startsWith('f"') || token.startsWith('"') || token.startsWith("'")) {
                    className = "code-string";
                  }

                  // Fix for partial strings split by tokenizer... skipping complex logic for simplicity
                  // Instead, let's just color specific known tokens for the demo

                  parts.push(<span key={idx} className={className}>{token}</span>);
                });

                if (comment) {
                  parts.push(<span key="comment" className="code-comment">{comment}</span>);
                }

                return parts;
              };

              // Better simple regex based highlighter for entire line
              const renderHighlightedLine = (text: string) => {
                if (!text) return <span> </span>;

                // Very basic parser:
                // 1. Strings
                // 2. Comments
                // 3. Keywords

                const tokens = [
                  { type: 'comment', regex: /#.*/ },
                  { type: 'string', regex: /"(?:[^"\\]|\\.)*"|'(?:[^'\\]|\\.)*'/ },
                  { type: 'keyword', regex: /\b(def|class|import|from|return|if|else|elif|try|except|print|in|as|with|for|while|break|continue|pass|lambda|global|nonlocal|assert|del|yield|raise)\b/ },
                  { type: 'function', regex: /\b([a-zA-Z_][a-zA-Z0-9_]*)(?=\()/ }, // word followed by (
                  { type: 'number', regex: /\b\d+\b/ },
                ];

                let result = [];
                let remaining = text;
                let key = 0;

                while (remaining.length > 0) {
                  let bestMatch = null;
                  let bestType = null;
                  let bestIdx = Infinity;

                  for (const token of tokens) {
                    const match = remaining.match(token.regex);
                    if (match && match.index !== undefined && match.index < bestIdx) {
                      bestMatch = match[0];
                      bestType = token.type;
                      bestIdx = match.index;
                    }
                  }

                  // If comment is found, it overrides everything inside it?
                  // Actually comments should be checked first or regex priority matters. 
                  // Simple workaround: Just use a library? No.

                  // Split by the first match found
                  if (bestMatch && bestIdx !== Infinity) {
                    // Push text before match
                    if (bestIdx > 0) {
                      result.push(<span key={key++} className="text-foreground">{remaining.slice(0, bestIdx)}</span>);
                    }
                    // Push match
                    let className = "text-foreground";
                    if (bestType === 'keyword') className = "code-keyword font-semibold";
                    if (bestType === 'string') className = "code-string";
                    if (bestType === 'comment') className = "code-comment italic";
                    if (bestType === 'function') className = "code-function";
                    if (bestType === 'number') className = "text-[#098658]";

                    result.push(<span key={key++} className={className}>{bestMatch}</span>);
                    remaining = remaining.slice(bestIdx + bestMatch.length);
                  } else {
                    // No matches
                    result.push(<span key={key++} className="text-foreground">{remaining}</span>);
                    break;
                  }
                }
                return result;
              };

              return (
                <div
                  key={num}
                  className={`flex ${isHighlight ? 'bg-yellow-50/80 -mx-4 px-4 border-l-4 border-yellow-400' : ''}`}
                >
                  <span className="code-line-number text-right pr-4 text-xs tabular-nums opacity-50 select-none py-[1px]">{num}</span>
                  <div className="whitespace-pre font-mono code-variable flex-1">
                    {renderHighlightedLine(line)}
                  </div>
                  {isHighlight && <span className="text-yellow-600 ml-2 text-xs font-bold py-[1px]">⚠</span>}
                </div>
              );
            })}
          </div>
        )}
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between px-4 py-1.5 border-t bg-muted/30 text-xs text-muted-foreground">
        <div className="flex items-center">
          <span>Python 3.9</span>
          <span className="mx-2">|</span>
          <span>{codeContent ? `Ln ${lines.length}, Col 1` : 'No file'}</span>
          <span className="mx-2">|</span>
          <span>UTF-8</span>
        </div>
      </div>
    </div>
  );
}