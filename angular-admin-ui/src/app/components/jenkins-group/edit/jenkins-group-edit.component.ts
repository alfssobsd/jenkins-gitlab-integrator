import 'rxjs/add/operator/switchMap';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { Location }                 from '@angular/common';

import { JenkinsGroup } from '../../../models/jenkins-group'
import { JenkinsGroupService } from '../../../services/jenkins-group.service'
import { JenkinsJob } from "../../../models/jenkins-job";
import { JenkinsJobService } from "../../../services/jenkins-job.service";

@Component({
  selector: 'app-jenkins-group-edit',
  templateUrl: './jenkins-group-edit.component.html',
})
export class JenkinsGroupEditComponent implements OnInit {
  jenkinsGroup: JenkinsGroup;
  jenkinsJobList: JenkinsJob[];

  constructor(
    private jenkinsGroupService:JenkinsGroupService,
    private jenkinsJobServices: JenkinsJobService,
    private route: ActivatedRoute,
    private location: Location
  ) { }

  ngOnInit() {
    this.route.paramMap
      .switchMap((params: ParamMap) => this.jenkinsGroupService.getJenkinsGroup(+params.get('id')))
      .subscribe(group => this.jenkinsGroup = group);

    this.route.paramMap
      .switchMap((params: ParamMap) => this.jenkinsJobServices.getJenkinsJobs(+params.get('id')))
      .subscribe(jobs => this.jenkinsJobList = jobs);
  }

  save(): void {
    this.jenkinsGroupService.updateJenkinsGroup(this.jenkinsGroup.id, this.jenkinsGroup)
      .then(group => this.jenkinsGroup = group)
  }

  goBack(): void {
    this.location.back();
  }
}
