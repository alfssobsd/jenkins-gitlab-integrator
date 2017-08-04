import { Component, OnInit } from '@angular/core';
import { Router }            from '@angular/router';

import { JenkinsGroup } from '../../../models/jenkins-group'
import { JenkinsGroupService } from '../../../services/jenkins-group.service'

@Component({
  selector: 'app-jenkins-groups',
  templateUrl: './jenkins-groups.component.html',
})
export class JenkinsGroupsComponent implements OnInit {
  jenkinsGroupList: JenkinsGroup[];
  searchName: string;

  constructor(
    private jenkinsGroupService:JenkinsGroupService,
  ) { }

  ngOnInit() {
    this.jenkinsGroupService
      .searchJenkinsGroups(this.searchName)
      .then(groups => this.jenkinsGroupList = groups)
  }

  search() {
    this.jenkinsGroupService
      .searchJenkinsGroups(this.searchName)
      .then(groups => this.jenkinsGroupList = groups)
  }
}
