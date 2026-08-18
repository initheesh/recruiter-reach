export type GenerateApplicationRequest = {
  recruiter_name: string;
  recruiter_email: string;
  company_name: string;
  job_title: string;
  job_description: string;
  additional_context: string;
};

export type GenerateApplicationResponse = {
  subject: string;
  body: string;
};

export type SendApplicationRequest = {
  recruiter_name: string;
  recruiter_email: string;
  company_name: string;
  job_title: string;
  subject: string;
  body: string;
};

export type SendApplicationResponse = {
  success: boolean;
  message: string;
  gmail_message_id: string;
  gmail_thread_id: string;
  sent_email_id: number | null;
  db_persisted: boolean;
};

export type ApplicationListItemResponse = {
  id: number;
  recruiter_name: string;
  recruiter_email: string;
  company_name: string;
  job_title: string;
  subject: string;
  body: string;
  gmail_message_id: string;
  gmail_thread_id: string;
  status: string;
  sent_at: string;
  created_at: string;
};

export type ApiErrorPayload = {
  detail?: string;
};
