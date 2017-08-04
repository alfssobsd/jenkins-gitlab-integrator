import { Component, OnInit } from '@angular/core';
import { Router }            from '@angular/router';

import { DelayedTask } from '../../../models/delayed-task'
import { DelayedTaskService } from '../../../services/delayed-task.service'

@Component({
  selector: 'app-delayed-tasks',
  templateUrl: './delayed-tasks.component.html',
  styleUrls: ['./delayed-tasks.component.css']
})
export class DelayedTasksComponent implements OnInit {
  delayedTasks: DelayedTask[];
  searchData: DelayedTask;
  taskTypesList = [
      {name: 'GITLAB_MERGE_REQ'},
      {name: 'GITLAB_PUSH'}
    ];

  constructor(
    private delayedTaskService: DelayedTaskService
  ) { }

  ngOnInit() {
    this.initSearchData();
    this.delayedTaskService
      .searchDelayedTasks(this.searchData)
      .then(tasks => this.delayedTasks = tasks)
  }

  search() {
    console.log(this.searchData)
    this.delayedTaskService
      .searchDelayedTasks(this.searchData)
      .then(tasks => this.delayedTasks = tasks)
  }


  private initSearchData() {
    this.searchData = new DelayedTask();
    this.searchData.task_type = 'GITLAB_MERGE_REQ';
    this.searchData.group = null;
    this.searchData.job_name = null;
    this.searchData.branch = null;
    this.searchData.sha1 = null;
  }
}
