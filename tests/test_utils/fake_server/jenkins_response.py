def generate_last_successful_build(base_url = None, group_folder = None, job_name = None, branch = None, build_number = 1,
                                        upstream_job_name = None, upstream_build_number = 1, repo_url = None,
                                        result = "SUCCESS"):
    data = {
        "_class": "org.jenkinsci.plugins.workflow.job.WorkflowRun",
        "actions":[
            {},
            {
                "_class": "hudson.plugins.git.util.BuildData",
                "buildsByBranchName": {
                    "lib-pipline-branch": {
                        "_class": "hudson.plugins.git.util.Build",
                        "buildNumber": build_number,
                        "buildResult": None,
                        "marked": {
                            "SHA1": "2e83e6a19d57bac6229c542c05ff98b3683c356e",
                            "branch": [
                                {
                                    "SHA1": "2e83e6a19d57bac6229c542c05ff98b3683c356e",
                                    "name": "lib-pipline-branch"
                                }
                            ]
                        },
                        "revision": {
                            "SHA1": "2e83e6a19d57bac6229c542c05ff98b3683c356e",
                            "branch": [
                                {
                                    "SHA1": "2e83e6a19d57bac6229c542c05ff98b3683c356e",
                                    "name": "lib-pipline-branch"
                                }
                            ]
                        }
                        }
                    },
                    "lastBuiltRevision": {
                        "SHA1": "2e83e6a19d57bac6229c542c05ff98b3683c356e",
                        "branch": [
                            {
                                "SHA1": "2e83e6a19d57bac6229c542c05ff98b3683c356e",
                                "name": "lib-pipline-branch"
                            }
                        ]
                    },
                    "remoteUrls": [
                        "ssh://git@gitlab.example.local:2222/DevOps/Jenkins/lib-pipeline-common.git"
                    ],
                    "scmName": ""
                },
            {
                "_class": "hudson.plugins.git.GitTagAction"
            },
            {},
            {
                "_class": "hudson.plugins.git.util.BuildData",
                "buildsByBranchName": {
                    branch: {
                        "_class": "hudson.plugins.git.util.Build",
                        "buildNumber": build_number,
                        "buildResult": None,
                        "marked": {
                            "SHA1": "0692f3f7f5f764a8a31b34ae768cb513ccc780b8",
                            "branch": [
                                {
                                    "SHA1": "0692f3f7f5f764a8a31b34ae768cb513ccc780b8",
                                    "name": branch
                                }
                            ]
                        },
                        "revision": {
                            "SHA1": "0692f3f7f5f764a8a31b34ae768cb513ccc780b8",
                            "branch": [
                                {
                                    "SHA1": "0692f3f7f5f764a8a31b34ae768cb513ccc780b8",
                                    "name": branch
                                }
                            ]
                        }
                    }
                },
                "lastBuiltRevision": {
                    "SHA1": "0692f3f7f5f764a8a31b34ae768cb513ccc780b8",
                    "branch": [
                        {
                            "SHA1": "0692f3f7f5f764a8a31b34ae768cb513ccc780b8",
                            "name": branch
                        }
                    ]
                },
                "remoteUrls": [
                    repo_url
                ],
                "scmName": ""
            },
            {}
        ],
        "artifacts": [],
        "building": False,
        "description": None,
        "displayName": "#%d" % build_number,
        "duration": 3110,
        "estimatedDuration": 2905,
        "executor": None,
        "fullDisplayName": "%s » %s » %s #%d" % (group_folder, job_name, branch, build_number),
        "id": build_number,
        "number": build_number,
        "result": result,
        "timestamp": 1499862406762,
        "url": "%s/job/%s/job/%s/job/%s/%d/" % (base_url, group_folder, job_name, branch, build_number),
    }

    if upstream_job_name:
        data['actions'].append(
            {
                "_class": "hudson.model.CauseAction",
                "causes": [
                            {
                                "_class": "hudson.model.Cause$UpstreamCause",
                                "shortDescription": "Started by upstream project \"%s/%s/%s\" build number %d" % (group_folder, job_name, branch, upstream_build_number),
                                "upstreamBuild": upstream_build_number,
                                "upstreamProject": "%s/%s/%s" % (group_folder, upstream_job_name, branch),
                                "upstreamUrl": "job/%s/job/%s/job/%s/" % (group_folder, upstream_job_name, branch)
                            }
                ]
            })
    return data
