import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule }   from '@angular/forms';
import { HttpModule }    from '@angular/http';

// companents
import { AppComponent }  from './app.component';
import { StatsService } from './services/stats.service';
// config
import { ConfigComponent } from './components/config/index/config.component';
import { ConfigService } from './services/config.service';
import { JenkinsGroupService } from './services/jenkins-group.service';
// jenkins groups
import { JenkinsGroupsComponent } from './components/jenkins-group/index/jenkins-groups.component';
import { JenkinsGroupEditComponent } from './components/jenkins-group/edit/jenkins-group-edit.component';
// delayed task
import { DelayedTasksComponent } from './components/delayed-task/index/delayed-tasks.component';
import { DelayedTaskService } from './services/delayed-task.service';
import { DelayedTaskDetailComponent } from './components/delayed-task/show/delayed-task-detail.component';
// guards
import { AuthGuard } from './guards/auth.guard'
// common services
import { AuthenticationService }  from './services/authentication.service';
import { AlertService }           from './services/alert.service';
// common components
import { LoginComponent }         from './components/login/login.component';
import { AlertComponent }         from './components/alert/alert.component';
// pipe
import { KeysPipe } from './pipes/keys.pipe';
// routing
import { AppRoutingModule } from './app-routing.module';


@NgModule({
  declarations: [
    AppComponent,
    ConfigComponent,
    DelayedTasksComponent,
    DelayedTaskDetailComponent,
    KeysPipe,
    JenkinsGroupsComponent,
    JenkinsGroupEditComponent,
    LoginComponent,
    AlertComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    AppRoutingModule
  ],
  providers: [
    AuthGuard,
    AuthenticationService,
    AlertService,
    StatsService,
    ConfigService,
    DelayedTaskService,
    JenkinsGroupService
  ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
