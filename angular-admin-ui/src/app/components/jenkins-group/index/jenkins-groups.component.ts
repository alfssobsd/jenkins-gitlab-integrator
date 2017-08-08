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
  newJenkinsGroup: JenkinsGroup;

  constructor(
    private jenkinsGroupService:JenkinsGroupService,
    private router: Router,
  ) {
    this.newJenkinsGroup = new JenkinsGroup();
  }

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

  create() {
    this.jenkinsGroupService.createJenkinsGroup(this.newJenkinsGroup)
      .then(group => { this.router.navigate(['jenkins-groups', group.id]) })
  }

  delete(group: JenkinsGroup) {
    if(confirm("Are you sure to delete group "+group.name)) {
      this.jenkinsGroupService.deleteJenkinsGroup(group.id)
      .then(() => {
        this.jenkinsGroupList = this.jenkinsGroupList.filter(g => g !== group);
      });
    }
  }
}
