import 'rxjs/add/operator/switchMap';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { Location }                 from '@angular/common';
import { ToastyService }            from "ng2-toasty";

import { JenkinsGroup } from '../../../models/jenkins-group'
import { JenkinsGroupService } from '../../../services/jenkins-group.service'


@Component({
  selector: 'app-jenkins-group-edit',
  templateUrl: './jenkins-group-edit.component.html',
})
export class JenkinsGroupEditComponent implements OnInit {
  jenkinsGroup: JenkinsGroup;
  test: number;

  constructor(
    private jenkinsGroupService:JenkinsGroupService,
    private toastyService:ToastyService,
    private route: ActivatedRoute,
    private location: Location,
  ) { }

  ngOnInit() {
    this.route.paramMap
      .switchMap((params: ParamMap) => this.jenkinsGroupService.getJenkinsGroup(+params.get('id')))
      .subscribe(group => this.jenkinsGroup = group);
  }

  save(): void {
    this.jenkinsGroupService.updateJenkinsGroup(this.jenkinsGroup.id, this.jenkinsGroup)
      .then(group => {
        this.jenkinsGroup = group;
        this.toastyService.success("Group " + group.name + " is updated");
      })
      .catch(err => this.errorMessage(err));
  }

  goBack(): void {
    this.location.back();
  }

  private errorMessage(error){
    this.toastyService.error(error.statusText + " status: " + error.status)
  }
}
