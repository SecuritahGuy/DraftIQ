// API Types for DraftIQ Frontend

export interface User {
  id: string;
  email: string;
  username: string;
  display_name: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
  updated_at: string;
}

export interface YahooToken {
  id: string;
  user_id: string;
  access_token: string;
  refresh_token?: string;
  expires_at: string;
  token_type: string;
  scope: string;
  created_at: string;
  updated_at: string;
}

export interface League {
  league_key: string;
  name: string;
  season: number;
  league_type: string;
  num_teams: number;
  is_finished: boolean;
  scoring_json: string;
  roster_positions_json: string;
  created_at: string;
  updated_at: string;
}

export interface Team {
  team_key: string;
  league_key: string;
  name: string;
  manager?: string;
  division_id?: number;
  rank?: number;
  wins: number;
  losses: number;
  ties: number;
  created_at: string;
  updated_at: string;
}

export interface Player {
  player_id_yahoo: string;
  gsis_id?: string;
  full_name: string;
  position: string;
  team?: string;
  created_at: string;
  updated_at: string;
}

export interface LeaguePlayer {
  league_key: string;
  player_id_yahoo: string;
  status: string;
  percent_rostered?: number;
  faab_cost_est?: number;
  owner_team_key?: string;
  created_at: string;
  updated_at: string;
}

export interface Roster {
  team_key: string;
  week: number;
  slot: string;
  player_id_yahoo?: string;
  is_starting: boolean;
  created_at: string;
  updated_at: string;
}

export interface WeeklyStats {
  gsis_id: string;
  season: number;
  week: number;
  team: string;
  opponent?: string;
  game_date?: string;
  stats: Record<string, any>;
  fantasy_points: number;
}

export interface WeeklyProjections {
  gsis_id: string;
  season: number;
  week: number;
  source: string;
  projections: Record<string, any>;
  confidence?: number;
  created_at: string;
}

export interface Injuries {
  gsis_id: string;
  season: number;
  week: number;
  status: string;
  report?: string;
  practice_status?: string;
  team: string;
  position: string;
  is_out: boolean;
  is_questionable: boolean;
}

export interface DepthCharts {
  team: string;
  season: number;
  week: number;
  position: string;
  gsis_id: string;
  depth_order: number;
  role?: string;
  is_starter: boolean;
}

export interface ScoringRule {
  stat: string;
  points: number;
  threshold?: number;
  max_points?: number;
  tier_rules?: Array<{
    min: number;
    max: number;
    points: number;
  }>;
}

export interface ScoringSystem {
  passing_yards?: ScoringRule;
  passing_tds?: ScoringRule;
  passing_ints?: ScoringRule;
  rushing_yards?: ScoringRule;
  rushing_tds?: ScoringRule;
  receiving_yards?: ScoringRule;
  receiving_tds?: ScoringRule;
  receptions?: ScoringRule;
  fumbles_lost?: ScoringRule;
  field_goals?: ScoringRule;
  extra_points?: ScoringRule;
}

export interface FantasyPointsResponse {
  gsis_id: string;
  season: number;
  week: number;
  fantasy_points: number;
  scoring_breakdown: Record<string, number>;
  scoring_system: ScoringSystem;
}

// API Response Types
export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  message?: string;
  error?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  per_page: number;
  pages: number;
}

// Error Types
export interface ApiError {
  detail: string;
  status_code: number;
}

// Auth Types
export interface AuthStatus {
  authenticated: boolean;
  user?: User;
  yahoo_token?: YahooToken;
}

export interface OAuthStartResponse {
  success: boolean;
  authorization_url: string;
  state: string;
}

export interface OAuthCallbackResponse {
  success: boolean;
  user_id?: string;
  message?: string;
}
