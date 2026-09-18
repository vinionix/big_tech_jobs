import { apiRequest } from "@/lib/api";

export interface Account {
  id: string;
  email: string;
  created_at: string;
}

export interface Profile {
  id: string;
  user_id: string;
  full_name: string | null;
  phone: string | null;
  current_location: string | null;
  professional_summary: string | null;
  current_seniority: string | null;
  years_experience: string | null;
  countries_of_interest: string[];
  acceptable_timezones: string[];
  desired_work_modes: ("remote" | "hybrid" | "onsite")[];
  work_authorizations: string[];
  needs_sponsorship: boolean | null;
  willing_to_relocate: boolean | null;
  salary_min: number | null;
  salary_max: number | null;
  salary_currency: string | null;
  onboarding_step: number;
  onboarding_completed: boolean;
}

export interface Experience {
  id: string;
  company: string;
  title: string;
  start_date: string;
  end_date: string | null;
  is_current: boolean;
  responsibilities: string | null;
  results: string | null;
}

export interface Skill {
  id: string;
  name: string;
  category: "technical" | "behavioral";
  proficiency: string | null;
  years_experience: string | null;
}

export interface Project {
  id: string;
  title: string;
  description: string | null;
  role: string | null;
  results: string | null;
  url: string | null;
}

export interface Education {
  id: string;
  institution: string;
  degree: string | null;
  field_of_study: string | null;
  start_date: string | null;
  end_date: string | null;
}

export interface Language {
  id: string;
  name: string;
  proficiency: string;
}

export interface Certification {
  id: string;
  name: string;
  issuer: string | null;
  issue_date: string | null;
  credential_url: string | null;
}

export interface ProfessionalLink {
  id: string;
  label: string;
  url: string;
  kind: "portfolio" | "publication" | "profile";
}

export interface CareerGoal {
  id: string;
  target_title: string;
  area: string;
  target_seniority: string | null;
  priority: number;
}

export interface SearchPreferences {
  id: string;
  user_id: string;
  desired_job_count: number;
  frequency: "manual" | "daily" | "weekly" | "biweekly";
  max_recommendations: number;
  search_breadth: "focused" | "balanced" | "broad";
  minimum_score: string;
  preferred_company_types: string[];
  preferred_company_sizes: string[];
  preferred_sectors: string[];
  preferred_companies: string[];
  blocked_companies: string[];
  culture_preferences: string[];
  benefit_preferences: string[];
  work_nature_preferences: string[];
  elimination_criteria: string[];
}

export interface Onboarding {
  account: Account;
  profile: Profile;
  experiences: Experience[];
  projects: Project[];
  education: Education[];
  skills: Skill[];
  languages: Language[];
  certifications: Certification[];
  professional_links: ProfessionalLink[];
  career_goals: CareerGoal[];
  search_preferences: SearchPreferences;
  completeness: { percentage: number; missing: string[] };
}

export const splitList = (value: string): string[] =>
  value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);

export const getOnboarding = (): Promise<Onboarding> => apiRequest("/onboarding");
