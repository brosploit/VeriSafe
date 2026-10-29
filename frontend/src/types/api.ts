export type RiskLevel = 'Low' | 'Medium' | 'High' | 'Needs Review';
export type Channel = 'email' | 'sms' | 'chat' | 'social' | 'other';
export type AnalysisMode = 'message' | 'url';

export interface Indicator {
  category: string;
  signal: string;
  severity: 'low' | 'medium' | 'high' | 'critical';
  explanation: string;
  matched_text?: string;
}

export interface CommonAnalysis {
  analysis_id: string;
  timestamp: string;
  risk_level: RiskLevel;
  confidence_score: number;
  assessment_disclaimer: string;
  summary: string;
  indicators: Indicator[];
  recommendations: string[];
}

export interface MessageAnalysis extends CommonAnalysis {
  input_summary: {
    channel?: string;
    char_count?: number;
    detected_urls?: string[];
    [key: string]: unknown;
  };
}

export interface UrlAnalysis extends CommonAnalysis {
  target_url: string;
  normalized_url?: string;
  domain_details?: {
    domain?: string;
    tld?: string;
    subdomains?: string[];
    is_ip_address?: boolean;
    has_homoglyphs?: boolean;
  };
}

export type AnalysisResult = MessageAnalysis | UrlAnalysis;

export interface ApiErrorShape {
  error?: {
    code?: string;
    message?: string;
    details?: Array<{ field?: string; issue?: string }>;
  };
  detail?: string | Array<{ loc?: Array<string | number>; msg?: string }>;
}
