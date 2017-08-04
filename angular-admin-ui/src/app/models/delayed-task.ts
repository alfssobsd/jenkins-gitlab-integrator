export class DelayedTask {
  id: number;
  task_status: string;
  task_type: string;
  group: string;
  job_name: string;
  branch: string;
  sha1: string;
  counter_attempts: number;
  gitlab_merge_comment_id: number;
}
