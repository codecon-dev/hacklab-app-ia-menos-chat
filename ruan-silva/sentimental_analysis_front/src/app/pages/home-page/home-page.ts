import { Component } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { CommonModule } from '@angular/common';
import { FormsModule } from '@angular/forms';
import { HttpClientModule } from '@angular/common/http';
import { HttpHeaders } from '@angular/common/http';

@Component({
  selector: 'app-home-page',
  imports: [
    CommonModule,
    FormsModule,
    HttpClientModule
  ],
  templateUrl: './home-page.html',
  styleUrl: './home-page.scss'
})
export class HomePage {
  message: string = '';
  result: string = 'Nenhum resultado.';
  oldMessage: string = 'Nenhuma mensagem enviada.';

  constructor(private http: HttpClient) {}

  sendMessage() {
    this.result = 'Carregando...';

    if (!this.message.trim()) return;

    const userMessage = this.message;
    this.oldMessage = this.message;
    this.message = '';
    const token = sessionStorage.getItem("access");

    this.http.post<{ message: string }>('http://localhost:8000/api/v1/analysis/', { message: userMessage }, { headers: new HttpHeaders({'Authorization': `Bearer ${token}`}) })
      .subscribe({
        next: (res) => {
          this.result = res.message;
        },
        error: () => {
          this.result = 'Erro ao enviar mensagem.';
        }
      });
  }
}
