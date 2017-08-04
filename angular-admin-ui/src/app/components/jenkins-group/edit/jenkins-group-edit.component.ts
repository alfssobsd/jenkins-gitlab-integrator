import 'rxjs/add/operator/switchMap';
import { Component, OnInit } from '@angular/core';
import { ActivatedRoute, ParamMap } from '@angular/router';
import { Location }                 from '@angular/common';

import { JenkinsGroup } from '../../../models/jenkins-group'
import { JenkinsGroupService } from '../../../services/jenkins-group.service'

@Component({
  selector: 'app-jenkins-group-edit',
  templateUrl: './jenkins-group-edit.component.html',
  styleUrls: ['./jenkins-group-edit.component.css']
})
export class JenkinsGroupEditComponent implements OnInit {
  jenkinsGroup: JenkinsGroup;

  constructor(
    private jenkinsGroupService:JenkinsGroupService,
    private route: ActivatedRoute,
    private location: Location
  ) { }

  ngOnInit() {
    this.route.paramMap
      .switchMap((params: ParamMap) => this.jenkinsGroupService.getJenkinsGroup(+params.get('id')))
      .subscribe(group => this.jenkinsGroup = group);
  }

  save(): void {

  }

  goBack(): void {
    this.location.back();
  }
}
