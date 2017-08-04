import 'rxjs/add/operator/switchMap';
import { Component, OnInit }        from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { Location }                 from '@angular/common';

import { DelayedTask }        from './delayed-task'
import { DelayedTaskService } from './delayed-task.service'

@Component({
  selector: 'app-delayed-task-detail',
  templateUrl: './delayed-task-detail.component.html',
  styleUrls: ['./delayed-task-detail.component.css']
})
export class DelayedTaskDetailComponent implements OnInit {
  delayedTask: DelayedTask;

  constructor(
    private delayedTaskService: DelayedTaskService,
    private route: ActivatedRoute,
    private location: Location
  ) { }

  ngOnInit() {
    this.route.paramMap
      .switchMap((params: ParamMap) => this.delayedTaskService.getDelayedTask(+params.get('id')))
      .subscribe(delayedTask => this.delayedTask = delayedTask);
  }

  setStatus(status: string): void {
    this.delayedTaskService.setDelayedTaskStatus(this.delayedTask.id, status)
      .then(delayedTask => this.delayedTask = delayedTask)
  }

  goBack(): void {
    this.location.back();
  }

}
