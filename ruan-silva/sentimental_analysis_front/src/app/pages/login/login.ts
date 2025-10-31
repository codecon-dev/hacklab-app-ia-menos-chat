import { Component } from '@angular/core';
import { DefaultLogin } from '../../components/default-login/default-login';
import { FormControl, FormGroup, ReactiveFormsModule, Validators } from '@angular/forms';
import { PrimaryInputComponent } from '../../components/primary-input/primary-input';
import { Router } from '@angular/router';
import { LoginService } from '../../services/login.service';
import { ToastrService } from 'ngx-toastr';
import { HttpClientModule } from '@angular/common/http';

interface LoginForm {
  username: FormControl,
  password: FormControl
}

@Component({
  selector: 'app-login',
  imports: [
    DefaultLogin,
    ReactiveFormsModule,
    PrimaryInputComponent,
    HttpClientModule
  ],
  providers: [LoginService],
  templateUrl: './login.html',
  styleUrl: './login.scss'
})
export class LoginComponent {
  loginForm!: FormGroup<LoginForm>;

  constructor(
    private router: Router,
    private loginService: LoginService,
    private toastr: ToastrService
  ){
    this.loginForm = new FormGroup({
      username: new FormControl('', [Validators.required]),
      password: new FormControl('', [Validators.required, Validators.minLength(8)])
    })
  }

  submit(){
    this.loginService.login( this.loginForm.value.username, this.loginForm.value.password ).subscribe({
      next: () => this.router.navigate(['/']),
      error: () => this.toastr.error("Erro ao realizar login! Tente novamente mais tarde.")
    })
  }

  navigate(){
    // this.router.navigate(["signup"]);
    this.toastr.warning("Não implementado! Tente mais tarde.")
  }
}