export interface Job {
  id: string;
  title: string;
  department?: string;
  location?: string;
  remote_option: boolean;
  job_type: string;
  experience_level: string;
  description: string;
  optimized_description?: string;
  responsibilities: string[];
  benefits: string[];
  requirements: Requirement[];
  min_experience_years: number;
  salary?: {
    min?: number;
    max?: number;
    currency: string;
  };
  status: JobStatus;
  total_applicants: number;
  screened_count: number;
  shortlisted_count: number;
  interviewed_count: number;
  created_at: string;
  published_at?: string;
  application_link: string;
}

export interface Requirement {
  skill: string;
  level: string;
  required: boolean;
  weight?: number;
}

export type JobStatus = 'draft' | 'active' | 'paused' | 'closed' | 'filled';

export interface Candidate {
  id: string;
  job_id: string;
  name: string;
  email?: string;
  phone?: string;
  location?: string;
  linkedin_url?: string;
  github_url?: string;
  portfolio_url?: string;
  summary?: string;
  skills: Skill[];
  experiences: Experience[];
  education: Education[];
  total_experience_years: number;
  resume_path?: string;
  cover_letter?: string;
  status: CandidateStatus;
  match_score?: number;
  match_details?: MatchDetails;
  ai_assessment?: string;
  applied_at: string;
  screened_at?: string;
}

export interface Skill {
  name: string;
  level: string;
  years?: number;
}

export interface Experience {
  company: string;
  title: string;
  start_date?: string;
  end_date?: string;
  description?: string;
  achievements?: string[];
  is_current: boolean;
}

export interface Education {
  institution: string;
  degree: string;
  field_of_study?: string;
  graduation_year?: number;
  gpa?: number;
}

export type CandidateStatus =
  | 'applied'
  | 'screening'
  | 'shortlisted'
  | 'interview'
  | 'offered'
  | 'hired'
  | 'rejected'
  | 'withdrawn';

export interface MatchDetails {
  skill_matches: SkillMatch[];
  skill_coverage: number;
  matched_skills: string[];
  missing_skills: string[];
  bonus_skills: string[];
  strengths: string[];
  weaknesses: string[];
}

export interface SkillMatch {
  required_skill: string;
  candidate_skill?: string;
  match_score: number;
  is_match: boolean;
}

export interface ScreeningResults {
  job_id: string;
  job_title: string;
  total_applicants: number;
  screened_count: number;
  average_score: number;
  score_distribution: Record<string, number>;
  top_candidates: Array<{
    id: string;
    name: string;
    score: number;
    status: string;
  }>;
  qualified_count: number;
}
