import { Component } from '@angular/core';
import { AgentResponse, ApiService, InferResponse } from './api.service';
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
  queryLogResponse: { role: string, content: string }[] = [];
  loading: boolean = false;

  constructor(private apiService: ApiService) {}

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
        // res.messages.forEach((message) => {
        //   this.queryLogResponse.push(message);
        // });
        this.queryLogResponse = res.messages;

        // 關閉 loading 狀態
        this.loading = false;
      },
      error: (err) => {
        // 錯誤時顯示錯誤訊息
        this.queryLogResponse.push({ role: 'assistant', content: '發送請求失敗：' + (err?.message || '') });
        this.loading = false;
      },
    });
  }

}
