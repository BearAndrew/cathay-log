import { Component } from '@angular/core';
import { AgentResponse, ApiService, InferResponse, Message } from './api.service';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { MarkdownModule } from 'ngx-markdown';

@Component({
  selector: 'app-root',
  imports: [CommonModule, FormsModule, MarkdownModule],
  templateUrl: './app.component.html',
  styleUrl: './app.component.scss',
})
export class AppComponent {
  userInput = '';
  queryLogResponse: Message[] = [];
  loading: boolean = false;

  isComposing: boolean = false;
  canSubmit: boolean = true;
  private imeTimeout: any = null;

  constructor(private apiService: ApiService) {}

  onCompositionEnd() {
    this.isComposing = false;

    // 結束輸入後，延遲 50ms 才允許送出
    this.canSubmit = false;
    clearTimeout(this.imeTimeout);
    this.imeTimeout = setTimeout(() => {
      this.canSubmit = true;
    }, 50);
  }

  handleEnter() {
    if (this.isComposing || !this.canSubmit || this.loading) {
      return; // 還在輸入或 loading 狀態，不送出
    }

    this.queryLog();
  }
  queryLog() {
    if (this.userInput.trim() === '') return; // 不處理空輸入

    // 顯示使用者輸入的訊息
    this.queryLogResponse.push({ role: 'user', content: this.userInput });

    // 設定 loading 狀態，禁用按鈕
    this.loading = true;

    const input = this.userInput;

    // 清空用戶輸入框
    this.userInput = '';

    // 發送請求給 API
    this.apiService.queryLog(input).subscribe({
      next: (res) => {
        // 將 API 回應的訊息加入
        this.queryLogResponse.push({ role: res.message.role, content: res.message.content, tool_detail: res.tool_detail });

        // 關閉 loading 狀態
        this.loading = false;
      },
      error: (err) => {
        // 錯誤時顯示錯誤訊息
        this.queryLogResponse.push({
          role: 'assistant',
          content: '發送請求失敗：' + (err?.message || ''),
        });
        this.loading = false;
      },
    });
  }
}
