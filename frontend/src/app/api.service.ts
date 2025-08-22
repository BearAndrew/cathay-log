import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';
import { environment } from '../environments/environment';

export interface AgentRequest {
  input: string;
}

export interface ToolCallInfo {
  name: string;
  args: any;
  tool_call_id?: string | null;
}

export interface MessageInfo {
  type: string;
  content: string | null;
  tool_calls?: ToolCallInfo[] | null;
}

export interface AgentResponse {
  response: string;
  all_contents: MessageInfo[];
}

export interface InferResponse {
  messages: { role: string; content: string }[];
}

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private baseUrl = environment.apiUrl;
  session_id = Date.now().toString();


  constructor(private http: HttpClient) {}

  invokeAgent(input: string): Observable<AgentResponse> {
    const url = `${this.baseUrl}/web-log/invoke`;
    const body: AgentRequest = { input };
    return this.http.post<AgentResponse>(url, body);
  }

  queryLog(input: string): Observable<InferResponse> {
    const url = `${this.baseUrl}/api/infer`;

    const body = {
      input,
      session_id: this.session_id,
    };

    return this.http.post<InferResponse>(url, body);
  }
}
