import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

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
  private apiUrl = '/web-log/invoke';

  constructor(private http: HttpClient) {}

  invokeAgent(input: string): Observable<AgentResponse> {
    const body: AgentRequest = { input };
    return this.http.post<AgentResponse>(this.apiUrl, body);
  }

  queryLog(input: string): Observable<InferResponse> {
    const url = '/api/infer';

    // 取得或產生 session_id
    let session_id = localStorage.getItem('session_id');
    if (!session_id) {
      session_id = Date.now().toString(); // 或用 UUID
      localStorage.setItem('session_id', session_id);
    }

    const body = {
      input,
      session_id,
    };

    return this.http.post<InferResponse>(url, body);
  }
}
