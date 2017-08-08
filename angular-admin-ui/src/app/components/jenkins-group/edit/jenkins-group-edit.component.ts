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
  selectJenkinsJob: JenkinsJob;

  constructor(
    private jenkinsGroupService:JenkinsGroupService,
    private jenkinsJobServices: JenkinsJobService,
    private route: ActivatedRoute,
    private location: Location
  ) {
    this.selectJenkinsJob = new JenkinsJob();
  }

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

  editJob(job: JenkinsJob): void {
    this.selectJenkinsJob = job;
  }

  saveJob(): void {
    if (!this.selectJenkinsJob.id) {
      this.selectJenkinsJob.jenkins_group_id = this.jenkinsGroup.id
      this.jenkinsJobServices.createJenkinsJob(this.selectJenkinsJob)
        .then(job => {
          this.jenkinsJobList.push(job)
          this.selectJenkinsJob = new JenkinsJob();
        })
    } else {
      this.jenkinsJobServices.updateJenkinsJob(this.selectJenkinsJob)
        .then(job => {
          this.selectJenkinsJob = job;
          this.selectJenkinsJob = new JenkinsJob();
        })
    }
  }

  deleteJob(job: JenkinsJob): void {
    if(confirm("Are you sure to delete job "+job.name)) {
      this.jenkinsJobServices.deleteJenkinsJob(job)
      .then(() => {
        this.jenkinsJobList = this.jenkinsJobList.filter(j => j !== job);
      });
    }
  }

  goBack(): void {
    this.location.back();
  }

}
