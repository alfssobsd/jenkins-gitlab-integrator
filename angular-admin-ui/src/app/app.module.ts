import { NgModule }      from '@angular/core';
import { BrowserModule } from '@angular/platform-browser';
import { FormsModule }   from '@angular/forms';
import { HttpModule }    from '@angular/http';

// companents
import { AppComponent }  from './app.component';
// config
import { ConfigComponent } from './config/config.component';
import { ConfigService } from './config/config.service';
// gitlab webhooks
// delayed task
import { DelayedTasksComponent } from './delayed-task/delayed-tasks.component';
import { DelayedTaskService } from './delayed-task/delayed-task.service';

// routing
import { AppRoutingModule } from './app-routing.module';


@NgModule({
  declarations: [
    AppComponent,
    ConfigComponent,
    DelayedTasksComponent
  ],
  imports: [
    BrowserModule,
    FormsModule,
    HttpModule,
    AppRoutingModule
  ],
  providers: [
    ConfigService,
    DelayedTaskService
  ],
  bootstrap: [ AppComponent ]
})
export class AppModule { }
