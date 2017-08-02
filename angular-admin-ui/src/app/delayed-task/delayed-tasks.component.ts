import { Component, OnInit } from '@angular/core';
import { Router }            from '@angular/router';

import { DelayedTaskService } from './delayed-task.service'
import { DelayedTask } from './delayed-task'

@Component({
  selector: 'app-delayed-tasks',
  templateUrl: './delayed-tasks.component.html',
  styleUrls: ['./delayed-tasks.component.css']
})
export class DelayedTasksComponent implements OnInit {
  delayedTasks: DelayedTask[];
  // selectedHero: Hero;

  constructor(
    private delayedTaskService: DelayedTaskService
  ) { }

  ngOnInit() {
    this.delayedTaskService
      .getDelayedTasks()
      .then(tasks => this.delayedTasks = tasks)
  }

}
