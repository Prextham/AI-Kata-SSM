export interface User {
    id: number;
    email: string;
    username: string;
    is_admin: boolean;
  }
  
  export interface Sweet {
    id: number;
    name: string;
    category: string;
    price: number;
    quantity: number;
  }
  
  export interface LoginCredentials {
    username: string;
    password: string;
  }
  
  export interface RegisterData {
    email: string;
    username: string;
    password: string;
  }
  
  export interface AuthResponse {
    access_token: string;
    token_type: string;
  }
  
  export interface SweetFormData {
    name: string;
    category: string;
    price: number;
    quantity: number;
  }
  
  export interface SearchParams {
    name?: string;
    category?: string;
    min_price?: number;
    max_price?: number;
  }