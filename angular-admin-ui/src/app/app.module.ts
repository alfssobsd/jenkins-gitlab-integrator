import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule }   from '@angular/forms';
import { HttpModule }    from '@angular/http';
import { ToastyModule }  from 'ng2-toasty';
import { D3Service }     from 'd3-ng2-service';

// companents
import { AppComponent }  from './app.component';
import { StatsService } from './services/stats.service';
// config
import { ConfigComponent } from './components/config/index/config.component';
import { ConfigService } from './services/config.service';
// jenkins groups
import { JenkinsGroupService } from './services/jenkins-group.service';
import { JenkinsGroupsComponent } from './components/jenkins-group/index/jenkins-groups.component';
import { JenkinsGroupEditComponent } from './components/jenkins-group/edit/jenkins-group-edit.component';
import { JenkinsJobsGraphWidgetComponent } from './components/jenkins-jobs/graph-widget/jenkins-jobs-graph-widget.components';
// jenkins jobs
import { JenkinsJobService } from "./services/jenkins-job.service"
import { JenkinsJobsComponent } from "./components/jenkins-jobs/jenkins-jobs.component"

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
    JenkinsJobsGraphWidgetComponent,
    JenkinsJobsComponent,
    LoginComponent,
    AlertComponent
  ],
  imports: [
    BrowserModule,
    ToastyModule.forRoot(),
    FormsModule,
    HttpModule,
    AppRoutingModule
  ],
  providers: [
    D3Service,
    AuthGuard,
    AuthenticationService,
    AlertService,
    StatsService,
    ConfigService,
    DelayedTaskService,
    JenkinsGroupService,
    JenkinsJobService
  ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
