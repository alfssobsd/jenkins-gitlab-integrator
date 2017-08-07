import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { AuthGuard } from './guards/auth.guard'
import { LoginComponent } from './components/login/login.component';
import { ConfigComponent }   from './components/config/index/config.component';
import { JenkinsGroupsComponent } from './components/jenkins-group/index/jenkins-groups.component';
import { JenkinsGroupEditComponent } from './components/jenkins-group/edit/jenkins-group-edit.component';
import { DelayedTasksComponent } from './components/delayed-task/index/delayed-tasks.component';
import { DelayedTaskDetailComponent } from './components/delayed-task/show/delayed-task-detail.component';


const routes: Routes = [
  { path: '', redirectTo: '/config', pathMatch: 'full' },
  { path: 'login', component: LoginComponent },
  { path: 'config',  component: ConfigComponent, canActivate: [AuthGuard] },
  { path: 'delayed-tasks',  component: DelayedTasksComponent, canActivate: [AuthGuard] },
  { path: 'delayed-tasks/:id',  component: DelayedTaskDetailComponent, canActivate: [AuthGuard] },
  { path: 'jenkins-groups',  component: JenkinsGroupsComponent, canActivate: [AuthGuard] },
  { path: 'jenkins-groups/:id',  component: JenkinsGroupEditComponent, canActivate: [AuthGuard] },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
