import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ConfigComponent }   from './config/config.component';
import { DelayedTasksComponent } from './delayed-task/delayed-tasks.component';
import { DelayedTaskDetailComponent } from './delayed-task/delayed-task-detail.component';

const routes: Routes = [
  { path: '', redirectTo: '/config', pathMatch: 'full' },
  { path: 'config',  component: ConfigComponent },
  { path: 'delayed-tasks',  component: DelayedTasksComponent },
  { path: 'delayed-tasks/:id',  component: DelayedTaskDetailComponent },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
