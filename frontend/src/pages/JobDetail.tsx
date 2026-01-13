import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { ArrowLeft, Users, Play, Pause, Sparkles, CheckCircle, Edit3, X, Save } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { jobsApi, candidatesApi, screeningApi } from '../api/client';

export default function JobDetail() {
  const { jobId } = useParams<{ jobId: string }>();
  const queryClient = useQueryClient();
  const [screening, setScreening] = useState(false);
  const [optimizing, setOptimizing] = useState(false);
  const [optimizeResult, setOptimizeResult] = useState<string | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [editedDescription, setEditedDescription] = useState('');

  const { data: job, isLoading: jobLoading } = useQuery({
    queryKey: ['job', jobId],
    queryFn: () => jobsApi.get(jobId!).then((res) => res.data),
    enabled: !!jobId,
  });

  const { data: candidates, isLoading: candidatesLoading } = useQuery({
    queryKey: ['candidates', jobId],
    queryFn: () => candidatesApi.listForJob(jobId!).then((res: any) => res.data),
    enabled: !!jobId,
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ status }: { status: string }) => jobsApi.updateStatus(jobId!, status),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job', jobId] });
      queryClient.invalidateQueries({ queryKey: ['jobs'] });
    },
  });

  const screenMutation = useMutation({
    mutationFn: () => screeningApi.screenJob(jobId!),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['candidates', jobId] });
      queryClient.invalidateQueries({ queryKey: ['job', jobId] });
      setScreening(false);
    },
    onError: () => {
      setScreening(false);
    },
  });

  const optimizeMutation = useMutation({
    mutationFn: () => screeningApi.optimizeJD(jobId!),
    onSuccess: (response: any) => {
      setOptimizeResult(response.data.optimized_description);
      setOptimizing(false);
    },
    onError: () => {
      setOptimizing(false);
    },
  });

  const handleScreen = () => {
    setScreening(true);
    screenMutation.mutate();
  };

  const updateJobMutation = useMutation({
    mutationFn: (data: { description: string }) => jobsApi.update(jobId!, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['job', jobId] });
      setIsEditing(false);
      setOptimizeResult(null);
      setEditedDescription('');
    },
  });

  const handleOptimize = () => {
    setOptimizing(true);
    optimizeMutation.mutate();
  };

  const handleStartEdit = () => {
    setEditedDescription(job?.description || '');
    setIsEditing(true);
  };

  const handleSaveEdit = () => {
    updateJobMutation.mutate({ description: editedDescription });
  };

  const handleCancelEdit = () => {
    setIsEditing(false);
    setEditedDescription('');
  };

  const handleApplyOptimization = () => {
    if (optimizeResult) {
      updateJobMutation.mutate({ description: optimizeResult });
    }
  };

  const handleDismissOptimization = () => {
    setOptimizeResult(null);
  };

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

  if (jobLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (!job) {
    return (
      <div className="text-center py-12">
        <h2 className="text-xl font-semibold text-gray-900">Job not found</h2>
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
          <Link to="/jobs" className="text-gray-500 hover:text-gray-700">
            <ArrowLeft className="w-5 h-5" />
          </Link>
          <div>
            <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
            <p className="text-gray-500">
              {job.department} • {job.location} {job.remote_option && '• Remote'}
            </p>
          </div>
        </div>
        <div className="flex items-center space-x-3">
          <span className={`px-3 py-1 rounded-full text-sm font-medium ${
            job.status === 'active' ? 'bg-green-100 text-green-800' :
            job.status === 'paused' ? 'bg-yellow-100 text-yellow-800' :
            'bg-gray-100 text-gray-800'
          }`}>
            {job.status}
          </span>
          {job.status === 'active' ? (
            <button
              onClick={() => updateStatusMutation.mutate({ status: 'paused' })}
              className="flex items-center space-x-1 px-3 py-2 border border-yellow-500 text-yellow-600 rounded-md hover:bg-yellow-50"
            >
              <Pause className="w-4 h-4" />
              <span>Pause</span>
            </button>
          ) : (
            <button
              onClick={() => updateStatusMutation.mutate({ status: 'active' })}
              className="flex items-center space-x-1 px-3 py-2 border border-green-500 text-green-600 rounded-md hover:bg-green-50"
            >
              <Play className="w-4 h-4" />
              <span>Activate</span>
            </button>
          )}
        </div>
      </div>

      {/* Job Info & Actions */}
      <div className="grid grid-cols-3 gap-6">
        {/* Job Details */}
        <div className="col-span-2 space-y-6">
          <div className="bg-white rounded-lg shadow p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold text-gray-900">Job Description</h2>
              <div className="flex items-center space-x-2">
                {!isEditing && !optimizeResult && (
                  <>
                    <button
                      onClick={handleStartEdit}
                      className="flex items-center space-x-1 px-3 py-1.5 text-gray-600 border border-gray-300 text-sm rounded-md hover:bg-gray-50"
                    >
                      <Edit3 className="w-4 h-4" />
                      <span>Edit</span>
                    </button>
                    <button
                      onClick={handleOptimize}
                      disabled={optimizing || optimizeMutation.isPending}
                      className="flex items-center space-x-2 px-3 py-1.5 bg-gradient-to-r from-purple-600 to-indigo-600 text-white text-sm rounded-md hover:from-purple-700 hover:to-indigo-700 disabled:opacity-50"
                    >
                      {optimizing || optimizeMutation.isPending ? (
                        <>
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                          <span>Analyzing...</span>
                        </>
                      ) : (
                        <>
                          <Sparkles className="w-4 h-4" />
                          <span>Optimize with AI</span>
                        </>
                      )}
                    </button>
                  </>
                )}
                {isEditing && (
                  <>
                    <button
                      onClick={handleCancelEdit}
                      className="flex items-center space-x-1 px-3 py-1.5 text-gray-600 border border-gray-300 text-sm rounded-md hover:bg-gray-50"
                    >
                      <X className="w-4 h-4" />
                      <span>Cancel</span>
                    </button>
                    <button
                      onClick={handleSaveEdit}
                      disabled={updateJobMutation.isPending}
                      className="flex items-center space-x-1 px-3 py-1.5 bg-green-600 text-white text-sm rounded-md hover:bg-green-700 disabled:opacity-50"
                    >
                      <Save className="w-4 h-4" />
                      <span>{updateJobMutation.isPending ? 'Saving...' : 'Save'}</span>
                    </button>
                  </>
                )}
              </div>
            </div>

            {isEditing ? (
              <textarea
                value={editedDescription}
                onChange={(e) => setEditedDescription(e.target.value)}
                rows={20}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary-500 text-sm"
                placeholder="Enter job description..."
              />
            ) : (
              <div className="prose prose-sm max-w-none text-gray-700">
                <ReactMarkdown
                  components={{
                    h1: ({ children }) => <h2 className="text-xl font-bold text-gray-900 mt-4 mb-2">{children}</h2>,
                    h2: ({ children }) => <h3 className="text-lg font-semibold text-gray-800 mt-3 mb-2">{children}</h3>,
                    h3: ({ children }) => <h4 className="text-md font-semibold text-gray-800 mt-2 mb-1">{children}</h4>,
                    p: ({ children }) => <p className="mb-3 text-gray-700">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                    li: ({ children }) => <li className="text-gray-700">{children}</li>,
                    strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                  }}
                >
                  {job.description}
                </ReactMarkdown>
              </div>
            )}
          </div>

          {/* AI Optimized Version - Show when optimization is complete */}
          {optimizeResult && (
            <div className="bg-gradient-to-r from-green-50 to-emerald-50 rounded-lg shadow p-6 border-2 border-green-300">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-2">
                  <Sparkles className="w-5 h-5 text-green-600" />
                  <h2 className="text-lg font-semibold text-green-900">AI-Optimized Job Description</h2>
                  <span className="px-2 py-0.5 bg-green-100 text-green-700 text-xs rounded-full">New</span>
                </div>
              </div>

              <div className="bg-white rounded-lg p-4 mb-4 border border-green-200 max-h-96 overflow-y-auto">
                <div className="prose prose-sm max-w-none text-gray-700">
                  <ReactMarkdown
                    components={{
                      h1: ({ children }) => <h2 className="text-xl font-bold text-gray-900 mt-4 mb-2">{children}</h2>,
                      h2: ({ children }) => <h3 className="text-lg font-semibold text-gray-800 mt-3 mb-2">{children}</h3>,
                      h3: ({ children }) => <h4 className="text-md font-semibold text-gray-800 mt-2 mb-1">{children}</h4>,
                      p: ({ children }) => <p className="mb-3 text-gray-700">{children}</p>,
                      ul: ({ children }) => <ul className="list-disc list-inside mb-3 space-y-1">{children}</ul>,
                      ol: ({ children }) => <ol className="list-decimal list-inside mb-3 space-y-1">{children}</ol>,
                      li: ({ children }) => <li className="text-gray-700">{children}</li>,
                      strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                    }}
                  >
                    {optimizeResult}
                  </ReactMarkdown>
                </div>
              </div>

              <div className="flex items-center justify-between pt-4 border-t border-green-200">
                <p className="text-sm text-green-700">
                  Review the optimized version above. Click "Apply" to replace your current job description.
                </p>
                <div className="flex items-center space-x-3">
                  <button
                    onClick={handleDismissOptimization}
                    className="px-4 py-2 text-gray-600 border border-gray-300 rounded-md hover:bg-gray-50"
                  >
                    Dismiss
                  </button>
                  <button
                    onClick={handleApplyOptimization}
                    disabled={updateJobMutation.isPending}
                    className="px-4 py-2 bg-green-600 text-white rounded-md hover:bg-green-700 disabled:opacity-50 flex items-center space-x-2"
                  >
                    <CheckCircle className="w-4 h-4" />
                    <span>{updateJobMutation.isPending ? 'Applying...' : 'Apply Changes'}</span>
                  </button>
                </div>
              </div>
            </div>
          )}

          {job.requirements && job.requirements.length > 0 && (
            <div className="bg-white rounded-lg shadow p-6">
              <h2 className="text-lg font-semibold text-gray-900 mb-4">Requirements</h2>
              <div className="flex flex-wrap gap-2">
                {job.requirements.map((req: any, index: number) => (
                  <span
                    key={index}
                    className={`px-3 py-1 rounded-full text-sm ${
                      req.required ? 'bg-primary-100 text-primary-800' : 'bg-gray-100 text-gray-700'
                    }`}
                  >
                    {req.skill} ({req.level})
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Application Link */}
          <div className="bg-white rounded-lg shadow p-6">
            <h2 className="text-lg font-semibold text-gray-900 mb-4">Application Link</h2>
            <div className="flex items-center space-x-2">
              <input
                type="text"
                readOnly
                value={`${window.location.origin}/apply/${job.id}`}
                className="flex-1 px-3 py-2 border border-gray-300 rounded-md bg-gray-50"
              />
              <button
                onClick={() => navigator.clipboard.writeText(`${window.location.origin}/apply/${job.id}`)}
                className="px-4 py-2 bg-primary-600 text-white rounded-md hover:bg-primary-700"
              >
                Copy
              </button>
            </div>
            <p className="text-sm text-gray-500 mt-2">Share this link with candidates to receive applications.</p>
          </div>
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Stats */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">Statistics</h3>
            <div className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Total Applicants</span>
                <span className="font-semibold">{job.total_applicants || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Screened</span>
                <span className="font-semibold">{job.screened_count || 0}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-gray-600">Shortlisted</span>
                <span className="font-semibold">{job.shortlisted_count || 0}</span>
              </div>
            </div>
          </div>

          {/* Actions */}
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-semibold text-gray-900 mb-4">AI Screening</h3>
            <button
              onClick={handleScreen}
              disabled={screening || screenMutation.isPending}
              className="w-full px-4 py-3 bg-gradient-to-r from-primary-600 to-primary-700 text-white rounded-md hover:from-primary-700 hover:to-primary-800 disabled:opacity-50 flex items-center justify-center space-x-2"
            >
              {screening || screenMutation.isPending ? (
                <>
                  <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white"></div>
                  <span>Screening...</span>
                </>
              ) : (
                <>
                  <Play className="w-4 h-4" />
                  <span>Run AI Screening</span>
                </>
              )}
            </button>
            <p className="text-sm text-gray-500 mt-2">
              AI agents will analyze resumes and match candidates to job requirements.
            </p>
          </div>
        </div>
      </div>

      {/* Candidates List */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b">
          <h2 className="text-lg font-semibold text-gray-900">Candidates</h2>
        </div>
        {candidatesLoading ? (
          <div className="p-6 text-center">
            <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-primary-600 mx-auto"></div>
          </div>
        ) : !candidates || candidates.length === 0 ? (
          <div className="p-6 text-center text-gray-500">
            <Users className="w-12 h-12 mx-auto mb-2 text-gray-400" />
            <p>No candidates have applied yet.</p>
            <p className="text-sm">Share the application link to receive applications.</p>
          </div>
        ) : (
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Candidate</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Match Score</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase">Applied</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase">Actions</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {candidates.map((candidate: any) => (
                <tr key={candidate.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="font-medium text-gray-900">{candidate.name}</div>
                    <div className="text-sm text-gray-500">{candidate.email}</div>
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 py-1 text-xs font-medium rounded-full ${getStatusColor(candidate.status)}`}>
                      {candidate.status.replace('_', ' ')}
                    </span>
                  </td>
                  <td className="px-6 py-4">
                    {candidate.match_score !== null ? (
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div
                            className={`h-2 rounded-full ${
                              candidate.match_score >= 80 ? 'bg-green-500' :
                              candidate.match_score >= 60 ? 'bg-yellow-500' :
                              'bg-red-500'
                            }`}
                            style={{ width: `${candidate.match_score}%` }}
                          ></div>
                        </div>
                        <span className="text-sm font-medium">{candidate.match_score}%</span>
                      </div>
                    ) : (
                      <span className="text-gray-400 text-sm">Not screened</span>
                    )}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {new Date(candidate.applied_at).toLocaleDateString('en-US', {
                      year: 'numeric',
                      month: 'short',
                      day: 'numeric'
                    })}
                  </td>
                  <td className="px-6 py-4 text-right">
                    <Link
                      to={`/candidates/${candidate.id}`}
                      className="text-primary-600 hover:text-primary-800 text-sm font-medium"
                    >
                      View Details
                    </Link>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </div>
  );
}
