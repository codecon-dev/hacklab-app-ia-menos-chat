import { Routes } from '@angular/router';
import { HomePage } from './pages/home-page/home-page';
import { LoginComponent } from './pages/login/login';
import { Register } from './pages/register/register';
import { AuthGuard } from './guards/auth.guard';

export const routes: Routes = [
    {
        path: "",
        component: HomePage,
        canActivate: [AuthGuard]
    },
    {
        path: "login",
        component: LoginComponent
    },
];
