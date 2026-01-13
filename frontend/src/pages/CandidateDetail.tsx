import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Mail, Phone, MapPin, Calendar, FileText, Star, CheckCircle, XCircle, Send, RefreshCw } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { candidatesApi } from '../api/client';

export default function CandidateDetail() {
  const { candidateId } = useParams<{ candidateId: string }>();
  const queryClient = useQueryClient();
  const [emailStatus, setEmailStatus] = useState<string | null>(null);

  const { data: candidate, isLoading } = useQuery({
    queryKey: ['candidate', candidateId],
    queryFn: () => candidatesApi.get(candidateId!).then((res) => res.data),
    enabled: !!candidateId,
  });

  const updateStatusMutation = useMutation({
    mutationFn: (status: string) => candidatesApi.updateStatus(candidateId!, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidate', candidateId] });
      if (candidate?.job_id) {
        queryClient.invalidateQueries({ queryKey: ['candidates', candidate.job_id] });
        queryClient.invalidateQueries({ queryKey: ['job', candidate.job_id] });
      }
    },
  });

  const sendAssessmentMutation = useMutation({
    mutationFn: () => candidatesApi.sendAssessment(candidateId!),
    onSuccess: (response: any) => {
      const data = response.data;
      if (data.test_mode) {
        setEmailStatus(`Test Mode: Email preview generated for ${data.preview?.to || candidate?.email}. Verify domain at resend.com to send real emails.`);
      } else {
        setEmailStatus('Assessment email sent successfully!');
      }
      setTimeout(() => setEmailStatus(null), 8000);
    },
    onError: (error: any) => {
      setEmailStatus(`Failed: ${error.response?.data?.detail || 'Unknown error'}`);
      setTimeout(() => setEmailStatus(null), 5000);
    },
  });

  const sendInterviewMutation = useMutation({
    mutationFn: () => candidatesApi.sendInterviewInvite(candidateId!),
    onSuccess: (response: any) => {
      const data = response.data;
      queryClient.invalidateQueries({ queryKey: ['candidate', candidateId] });
      if (data.test_mode) {
        setEmailStatus(`Test Mode: Interview invite preview generated. Status updated to "Interview Scheduled". Verify domain to send real emails.`);
      } else {
        setEmailStatus('Interview invitation sent successfully!');
      }
      setTimeout(() => setEmailStatus(null), 8000);
    },
    onError: (error: any) => {
      setEmailStatus(`Failed: ${error.response?.data?.detail || 'Unknown error'}`);
      setTimeout(() => setEmailStatus(null), 5000);
    },
  });

  const rescreenMutation = useMutation({
    mutationFn: () => candidatesApi.rescreen(candidateId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidate', candidateId] });
      setEmailStatus('Candidate re-screened successfully!');
      setTimeout(() => setEmailStatus(null), 5000);
    },
    onError: (error: any) => {
      setEmailStatus(`Re-screen failed: ${error.response?.data?.detail || 'Unknown error'}`);
      setTimeout(() => setEmailStatus(null), 5000);
    },
  });

  const getStatusColor = (status: string) => {
    const colors: Record<string, string> = {
      applied: 'bg-gray-100 text-gray-800',
      screening: 'bg-blue-100 text-blue-800',
      shortlisted: 'bg-green-100 text-green-800',
      rejected: 'bg-red-100 text-red-800',
      interview_scheduled: 'bg-yellow-100 text-yellow-800',
      hired: 'bg-purple-100 text-purple-800',
    };
    return colors[status] || colors.applied;
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!candidate) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900">Candidate not found</h2>
        <Link to="/jobs" className="text-primary-600 hover:underline mt-2 inline-block">
          Back to Jobs
        </Link>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <Link
            to={candidate.job_id ? `/jobs/${candidate.job_id}` : '/jobs'}
            className="text-gray-500 hover:text-gray-700"
          >
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{candidate.name}</h1>
            <p className="text-gray-500">{candidate.email}</p>
          </div>
        </div>
        <span className={`px-3 py-1 rounded-full text-sm font-medium ${getStatusColor(candidate.status)}`}>
          {candidate.status.replace('_', ' ')}
        </span>
      </div>

      <div className="grid grid-cols-3 gap-6">
        {/* Main Content */}
        <div className="col-span-2 space-y-6">
          {/* Match Score */}
          {candidate.match_score !== null && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Match Score</h2>
              <div className="flex items-center space-x-6">
                <div className="relative w-32 h-32">
                  <svg className="w-32 h-32 transform -rotate-90">
                    <circle
                      cx="64"
                      cy="64"
                      r="56"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      className="text-gray-200"
                    />
                    <circle
                      cx="64"
                      cy="64"
                      r="56"
                      stroke="currentColor"
                      strokeWidth="8"
                      fill="none"
                      strokeDasharray={`${candidate.match_score * 3.52} 352`}
                      className={
                        candidate.match_score >= 80 ? 'text-green-500' :
                        candidate.match_score >= 60 ? 'text-yellow-500' :
                        'text-red-500'
                      }
                    />
                  </svg>
                  <div className="absolute inset-0 flex items-center justify-center">
                    <span className="text-3xl font-bold">{candidate.match_score}%</span>
                  </div>
                </div>
                <div className="flex-1">
                  <p className="text-gray-700">
                    {candidate.match_score >= 80
                      ? 'Excellent match! This candidate meets most of the job requirements.'
                      : candidate.match_score >= 60
                      ? 'Good match with some skill gaps. Consider for interview.'
                      : 'Below average match. May need significant training.'}
                  </p>
                </div>
              </div>
            </div>
          )}

          {/* Skills */}
          {candidate.skills && candidate.skills.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Skills</h2>
              <div className="flex flex-wrap gap-2">
                {candidate.skills.map((skill: any, index: number) => (
                  <span
                    key={index}
                    className="px-3 py-1 bg-primary-100 text-primary-800 rounded-full text-sm"
                  >
                    {skill.name} - {skill.level}
                    {skill.years_experience && ` (${skill.years_experience}y)`}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Experience */}
          {candidate.experiences && candidate.experiences.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Experience</h2>
              <div className="space-y-4">
                {candidate.experiences.map((exp: any, index: number) => (
                  <div key={index} className="border-l-2 border-primary-200 pl-4">
                    <h3 className="font-medium text-gray-900">{exp.title}</h3>
                    <p className="text-sm text-gray-600">{exp.company}</p>
                    <p className="text-sm text-gray-500">
                      {exp.start_date} - {exp.end_date || 'Present'}
                    </p>
                    {exp.description && (
                      <p className="text-sm text-gray-700 mt-2">{exp.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Education */}
          {candidate.education && candidate.education.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Education</h2>
              <div className="space-y-4">
                {candidate.education.map((edu: any, index: number) => (
                  <div key={index} className="border-l-2 border-gray-200 pl-4">
                    <h3 className="font-medium text-gray-900">{edu.degree}</h3>
                    <p className="text-sm text-gray-600">{edu.institution}</p>
                    {edu.field && <p className="text-sm text-gray-500">{edu.field}</p>}
                    {edu.year && <p className="text-sm text-gray-500">{edu.year}</p>}
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* AI Analysis */}
          {candidate.ai_assessment && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">AI Screening Analysis</h2>
              <div className="prose prose-sm max-w-none text-gray-700">
                <ReactMarkdown
                  components={{
                    h1: ({ children }) => <h3 className="text-lg font-bold text-gray-900 mt-4 mb-2">{children}</h3>,
                    h2: ({ children }) => <h4 className="text-md font-semibold text-gray-800 mt-3 mb-2">{children}</h4>,
                    h3: ({ children }) => <h5 className="text-sm font-semibold text-gray-800 mt-2 mb-1">{children}</h5>,
                    p: ({ children }) => <p className="mb-2 text-gray-700">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1">{children}</ul>,
                    li: ({ children }) => <li className="text-gray-700">{children}</li>,
                    strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                  }}
                >
                  {candidate.ai_assessment}
                </ReactMarkdown>
              </div>
            </div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Contact Info */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Contact</h3>
            <div className="space-y-3">
              <div className="flex items-center space-x-2 text-gray-600">
                <Mail className="w-4 h-4" />
                <span>{candidate.email}</span>
              </div>
              {candidate.phone && (
                <div className="flex items-center space-x-2 text-gray-600">
                  <Phone className="w-4 h-4" />
                  <span>{candidate.phone}</span>
                </div>
              )}
              {candidate.location && (
                <div className="flex items-center space-x-2 text-gray-600">
                  <MapPin className="w-4 h-4" />
                  <span>{candidate.location}</span>
                </div>
              )}
              <div className="flex items-center space-x-2 text-gray-600">
                <Calendar className="w-4 h-4" />
                <span>Applied {new Date(candidate.applied_at).toLocaleDateString('en-US', {
                    year: 'numeric',
                    month: 'short',
                    day: 'numeric',
                    hour: '2-digit',
                    minute: '2-digit'
                  })}</span>
              </div>
            </div>
          </div>

          {/* Resume */}
          {candidate.resume_path && (
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Resume</h3>
              <a
                href={`http://localhost:8000/api/candidates/${candidate.id}/resume`}
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center space-x-2 text-primary-600 hover:text-primary-800"
              >
                <FileText className="w-4 h-4" />
                <span>View Resume</span>
              </a>
            </div>
          )}

          {/* Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Actions</h3>
            <div className="space-y-3">
              {/* Email Status Message */}
              {emailStatus && (
                <div className={`p-3 rounded-md text-sm ${
                  emailStatus.includes('Failed')
                    ? 'bg-red-100 text-red-700'
                    : emailStatus.includes('Test Mode')
                      ? 'bg-yellow-100 text-yellow-800 border border-yellow-300'
                      : 'bg-green-100 text-green-700'
                }`}>
                  {emailStatus}
                </div>
              )}

              {/* Re-screen Button */}
              <button
                onClick={() => rescreenMutation.mutate()}
                disabled={rescreenMutation.isPending}
                className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
              >
                <RefreshCw className={`w-4 h-4 ${rescreenMutation.isPending ? 'animate-spin' : ''}`} />
                <span>{rescreenMutation.isPending ? 'Re-screening...' : 'Re-screen with AI'}</span>
              </button>

              {/* Send Assessment Email */}
              {candidate.match_score !== null && (
                <button
                  onClick={() => sendAssessmentMutation.mutate()}
                  disabled={sendAssessmentMutation.isPending}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 disabled:opacity-50"
                >
                  <Send className="w-4 h-4" />
                  <span>{sendAssessmentMutation.isPending ? 'Sending...' : 'Send Assessment Email'}</span>
                </button>
              )}

              {candidate.status !== 'shortlisted' && candidate.status !== 'hired' && (
                <button
                  onClick={() => updateStatusMutation.mutate('shortlisted')}
                  disabled={updateStatusMutation.isPending}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50"
                >
                  <CheckCircle className="w-4 h-4" />
                  <span>Shortlist</span>
                </button>
              )}
              {candidate.status !== 'rejected' && (
                <button
                  onClick={() => updateStatusMutation.mutate('rejected')}
                  disabled={updateStatusMutation.isPending}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 border border-red-500 text-red-600 rounded-md hover:bg-red-50 disabled:opacity-50"
                >
                  <XCircle className="w-4 h-4" />
                  <span>Reject</span>
                </button>
              )}
              {candidate.status === 'shortlisted' && (
                <>
                  <button
                    onClick={() => sendInterviewMutation.mutate()}
                    disabled={sendInterviewMutation.isPending}
                    className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-yellow-500 text-white rounded-md hover:bg-yellow-600 disabled:opacity-50"
                  >
                    <Calendar className="w-4 h-4" />
                    <span>{sendInterviewMutation.isPending ? 'Sending...' : 'Send Interview Invite'}</span>
                  </button>
                </>
              )}
              {candidate.status === 'interview_scheduled' && (
                <button
                  onClick={() => updateStatusMutation.mutate('hired')}
                  disabled={updateStatusMutation.isPending}
                  className="w-full flex items-center justify-center space-x-2 px-4 py-2 bg-purple-600 text-white rounded-md hover:bg-purple-700 disabled:opacity-50"
                >
                  <Star className="w-4 h-4" />
                  <span>Mark as Hired</span>
                </button>
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
