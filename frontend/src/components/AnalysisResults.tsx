import { Shield, AlertTriangle, AlertCircle, Search, Wand2 } from "lucide-react";
import { AnalysisResultsProps } from "@/types/security";
import { VulnerabilityCard } from "./VulnerabilityCard";
import { Button } from "@/components/ui/button";

export default function AnalysisResults({
  analysisResults,
  isAnalyzing,
  error,
  onFix
}: AnalysisResultsProps) {

  const criticalCount = analysisResults?.issues.filter(i => i.severity === 'critical').length || 0;
  const highCount = analysisResults?.issues.filter(i => i.severity === 'high').length || 0;
  const mediumCount = analysisResults?.issues.filter(i => i.severity === 'medium').length || 0;

  const severityCounts = [
    { icon: Shield, label: "Critical", count: criticalCount, bgClass: "bg-critical/15", textClass: "text-critical", visible: criticalCount > 0 },
    { icon: AlertTriangle, label: "High", count: highCount, bgClass: "bg-high/15", textClass: "text-high", visible: highCount > 0 },
    { icon: AlertCircle, label: "Medium", count: mediumCount, bgClass: "bg-medium/15", textClass: "text-medium", visible: mediumCount > 0 },
  ];

  return (
    <div className="flex flex-col h-full">
      <div className="bg-card rounded-lg border p-6 mb-6 shadow-sm mr-2">
        {/* Header Row */}
        <div className="flex items-start justify-between">
          <div className="mb-4 md:mb-0">
            <h2 className="text-2xl font-semibold text-foreground mb-1">Analysis Results</h2>
            <p className="text-sm text-muted-foreground mb-3">
              {analysisResults
                ? `Last scanned: just now. Found ${analysisResults.issues.length} vulnerabilities.`
                : 'Run analysis to see results'
              }
            </p>

            {/* Severity badges detected */}
            {analysisResults && analysisResults.issues.length > 0 && (
              <div className="flex gap-2">
                {severityCounts.filter(s => s.visible).map((item) => (
                  <div
                    key={item.label}
                    className={`flex items-center gap-1.5 px-2 py-1 rounded text-xs font-medium ${item.bgClass} ${item.textClass}`}
                  >
                    <item.icon className="w-3 h-3" />
                    <span className="font-medium">{item.label}: {item.count}</span>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="flex items-center gap-3">
            {/* Fix All Button */}
            {analysisResults && analysisResults.issues.length > 0 && (
              <Button
                size="sm"
                className="gap-1.5 bg-primary hover:bg-primary/90 text-primary-foreground order-1" // Primary color
                onClick={() => onFix(analysisResults.issues)}
                disabled={isAnalyzing}
              >
                <Wand2 className="w-4 h-4" />
                Fix All Issues
              </Button>
            )}
          </div>
        </div>
      </div>

      {/* Content */}
      <div className="flex-1 overflow-auto space-y-4 pr-2 scrollbar-thin">

        {/* Error */}
        {error && (
          <div className="bg-destructive/10 border border-destructive/20 rounded-lg p-4 text-destructive text-sm">
            {error}
          </div>
        )}

        {/* Empty State */}
        {!analysisResults && !error && !isAnalyzing && (
          <div className="h-full flex flex-col items-center justify-center text-center text-muted-foreground border-2 border-dashed rounded-xl p-8">
            <Wand2 className="w-12 h-12 mb-4 opacity-50" />
            <h3 className="text-lg font-medium mb-1">No Analysis Needed</h3>
            <p className="text-sm max-w-[200px]">Upload code and run analysis to see vulnerabilities here.</p>
          </div>
        )}

        {/* Loading */}
        {isAnalyzing && (
          <div className="h-full flex flex-col items-center justify-center">
            <div className="w-10 h-10 border-4 border-muted border-t-primary rounded-full animate-spin mb-4" />
            <p className="text-sm text-muted-foreground">Analyzing code structure...</p>
          </div>
        )}

        {/* Vulnerability list */}
        {analysisResults && !isAnalyzing && (
          analysisResults.issues.map((issue, index) => (
            <VulnerabilityCard
              key={index}
              severity={issue.severity as "critical" | "high" | "medium"}
              title={issue.title}
              description={issue.description}
              codeSnippet={issue.code}
              actionLabel="Fix Included in Fix All"
            // onAction removed to freeze individual buttons
            />
          ))
        )}
      </div>
    </div>
  );
}