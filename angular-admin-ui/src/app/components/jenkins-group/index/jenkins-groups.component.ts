import { Component, OnInit } from '@angular/core';
import { Router }            from '@angular/router';
import { ToastyService }     from "ng2-toasty";

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
    private toastyService:ToastyService,
    private router: Router,
  ) {
    this.newJenkinsGroup = new JenkinsGroup();
  }

  ngOnInit() {
    this.jenkinsGroupService
      .searchJenkinsGroups(this.searchName)
      .then(groups => this.jenkinsGroupList = groups)
      .catch(err => this.errorMessage(err));
  }

  searchGroup() {
    this.jenkinsGroupService
      .searchJenkinsGroups(this.searchName)
      .then(groups => this.jenkinsGroupList = groups)
      .catch(err => this.errorMessage(err));
  }

  createGroup() {
    this.jenkinsGroupService.createJenkinsGroup(this.newJenkinsGroup)
      .then(group => {
        this.toastyService.success("Group " + group.name + " is created");
        this.router.navigate(['jenkins-groups', group.id]);
      })
      .catch(err => this.errorMessage(err));
  }

  deleteGroup(group: JenkinsGroup) {
    if(confirm("Are you sure to delete group "+group.name)) {
      this.jenkinsGroupService.deleteJenkinsGroup(group.id)
      .then(() => {
        this.jenkinsGroupList = this.jenkinsGroupList.filter(g => g !== group);
        this.toastyService.success("Group " + group.name + " is deleted");
      })
      .catch(err => this.errorMessage(err));
    }
  }

  private errorMessage(error){
    this.toastyService.error("message: " + error.json().error + ", http_status: " + error.status)
  }
}
