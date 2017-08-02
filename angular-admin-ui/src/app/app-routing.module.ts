import { NgModule }             from '@angular/core';
import { RouterModule, Routes } from '@angular/router';

import { ConfigComponent }   from './config/config.component';
import { DelayedTasksComponent } from './delayed-tasks/delayed-tasks.component';

const routes: Routes = [
  { path: '', redirectTo: '/config', pathMatch: 'full' },
  { path: 'config',  component: ConfigComponent },
  { path: 'delayed-tasks',  component: DelayedTasksComponent },
];

@NgModule({
  imports: [ RouterModule.forRoot(routes) ],
  exports: [ RouterModule ]
})
export class AppRoutingModule {}
