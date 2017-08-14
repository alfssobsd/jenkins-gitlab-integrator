import { Component, OnInit } from '@angular/core';
import { Router }            from '@angular/router';
import { ToastyService }     from "ng2-toasty";

import { DelayedTask } from '../../../models/delayed-task'
import { DelayedTaskService } from '../../../services/delayed-task.service'


@Component({
  selector: 'app-delayed-tasks',
  templateUrl: './delayed-tasks.component.html',
})
export class DelayedTasksComponent implements OnInit {
  delayedTasks: DelayedTask[];
  searchData: DelayedTask;
  taskTypesList = [
      {name: 'GITLAB_MERGE_REQ'},
      {name: 'GITLAB_PUSH'}
    ];

  constructor(
    private delayedTaskService: DelayedTaskService,
    private toastyService:ToastyService,
  ) { }

  ngOnInit() {
    this.initSearchData();
    this.delayedTaskService
      .searchDelayedTasks(this.searchData)
      .then(tasks => this.delayedTasks = tasks)
      .catch(err => this.errorMessage(err));
  }

  search() {
    this.delayedTaskService
      .searchDelayedTasks(this.searchData)
      .then(tasks => this.delayedTasks = tasks)
      .catch(err => this.errorMessage(err));
  }


  private initSearchData() {
    this.searchData = new DelayedTask();
    this.searchData.task_type = 'GITLAB_MERGE_REQ';
    this.searchData.group = null;
    this.searchData.job_name = null;
    this.searchData.branch = null;
    this.searchData.sha1 = null;
  }

  private errorMessage(error){
    this.toastyService.error("message: " + error.json().error + ", http_status: " + error.status)
  }
}
