import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ConfigComponent }   from './components/config/index/config.component';
import { JenkinsGroupsComponent } from './components/jenkins-group/index/jenkins-groups.component';
import { JenkinsGroupEditComponent } from './components/jenkins-group/edit/jenkins-group-edit.component';
import { DelayedTasksComponent } from './components/delayed-task/index/delayed-tasks.component';
import { DelayedTaskDetailComponent } from './components/delayed-task/show/delayed-task-detail.component';


const routes: Routes = [
  { path: '', redirectTo: '/config', pathMatch: 'full' },
  { path: 'config',  component: ConfigComponent },
  { path: 'delayed-tasks',  component: DelayedTasksComponent },
  { path: 'delayed-tasks/:id',  component: DelayedTaskDetailComponent },
  { path: 'jenkins-groups',  component: JenkinsGroupsComponent },
  { path: 'jenkins-groups/:id',  component: JenkinsGroupEditComponent },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
