import { useState } from 'react';
import { useParams } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query';
import { Upload, CheckCircle, AlertCircle, Briefcase, MapPin } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { jobsApi, applyApi } from '../api/client';

export default function ApplyForm() {
  const { jobId } = useParams<{ jobId: string }>();
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    cover_letter: '',
  });
  const [resume, setResume] = useState<File | null>(null);
  const [submitted, setSubmitted] = useState(false);

  const { data: job, isLoading: jobLoading, error: jobError } = useQuery({
    queryKey: ['job-public', jobId],
    queryFn: () => jobsApi.get(jobId!).then((res) => res.data),
    enabled: !!jobId,
  });

  const applyMutation = useMutation({
    mutationFn: (data: FormData) => applyApi.submit(jobId!, data),
    onSuccess: () => {
      setSubmitted(true);
    },
  });

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files[0]) {
      setResume(e.target.files[0]);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!resume) return;

    const data = new FormData();
    data.append('name', formData.name);
    data.append('email', formData.email);
    data.append('phone', formData.phone);
    data.append('cover_letter', formData.cover_letter);
    data.append('resume', resume);

    applyMutation.mutate(data);
  };

  if (jobLoading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  if (jobError || !job) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-red-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Job Not Found</h1>
          <p className="text-gray-600">This job posting may have been removed or the link is invalid.</p>
        </div>
      </div>
    );
  }

  if (job.status !== 'active') {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-16 h-16 text-yellow-500 mx-auto mb-4" />
          <h1 className="text-2xl font-bold text-gray-900 mb-2">Position Closed</h1>
          <p className="text-gray-600">This job is no longer accepting applications.</p>
        </div>
      </div>
    );
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center max-w-md">
          <CheckCircle className="w-20 h-20 text-green-500 mx-auto mb-6" />
          <h1 className="text-3xl font-bold text-gray-900 mb-4">Application Submitted!</h1>
          <p className="text-gray-600 mb-6">
            Thank you for applying to <span className="font-semibold">{job.title}</span>.
            We'll review your application and get back to you soon.
          </p>
          <div className="text-sm text-gray-500">
            Reference ID: {jobId}-{Date.now().toString(36)}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Job Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-8">
          <div className="flex items-start space-x-4">
            <div className="w-12 h-12 bg-primary-100 rounded-lg flex items-center justify-center">
              <Briefcase className="w-6 h-6 text-primary-600" />
            </div>
            <div className="flex-1">
              <h1 className="text-2xl font-bold text-gray-900">{job.title}</h1>
              <div className="flex items-center space-x-4 text-gray-600 mt-2">
                {job.department && <span>{job.department}</span>}
                {job.location && (
                  <span className="flex items-center">
                    <MapPin className="w-4 h-4 mr-1" />
                    {job.location}
                  </span>
                )}
                {job.remote_option && (
                  <span className="px-2 py-1 bg-green-100 text-green-700 text-xs rounded-full">
                    Remote OK
                  </span>
                )}
              </div>
            </div>
          </div>

          {job.description && (
            <div className="mt-6 pt-6 border-t">
              <h2 className="font-semibold text-gray-900 mb-2">About this role</h2>
              <div className="prose prose-sm max-w-none text-gray-700">
                <ReactMarkdown
                  components={{
                    h1: ({ children }) => <h3 className="text-lg font-bold text-gray-900 mt-3 mb-2">{children}</h3>,
                    h2: ({ children }) => <h4 className="text-md font-semibold text-gray-800 mt-2 mb-1">{children}</h4>,
                    h3: ({ children }) => <h5 className="text-sm font-semibold text-gray-800 mt-2 mb-1">{children}</h5>,
                    p: ({ children }) => <p className="mb-2 text-gray-700 text-sm">{children}</p>,
                    ul: ({ children }) => <ul className="list-disc list-inside mb-2 space-y-1 text-sm">{children}</ul>,
                    ol: ({ children }) => <ol className="list-decimal list-inside mb-2 space-y-1 text-sm">{children}</ol>,
                    li: ({ children }) => <li className="text-gray-700">{children}</li>,
                    strong: ({ children }) => <strong className="font-semibold text-gray-900">{children}</strong>,
                  }}
                >
                  {job.description}
                </ReactMarkdown>
              </div>
            </div>
          )}

          {job.requirements && job.requirements.length > 0 && (
            <div className="mt-6 pt-6 border-t">
              <h2 className="font-semibold text-gray-900 mb-3">Required Skills</h2>
              <div className="flex flex-wrap gap-2">
                {job.requirements.map((req: any, index: number) => (
                  <span
                    key={index}
                    className={`px-3 py-1 rounded-full text-sm ${
                      req.required ? 'bg-primary-100 text-primary-700' : 'bg-gray-100 text-gray-600'
                    }`}
                  >
                    {req.skill}
                  </span>
                ))}
              </div>
            </div>
          )}
        </div>

        {/* Application Form */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <h2 className="text-xl font-bold text-gray-900 mb-6">Apply for this position</h2>

          <form onSubmit={handleSubmit} className="space-y-6">
            {/* Name */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Full Name *
              </label>
              <input
                type="text"
                required
                value={formData.name}
                onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="John Doe"
              />
            </div>

            {/* Email */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Email Address *
              </label>
              <input
                type="email"
                required
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="john@example.com"
              />
            </div>

            {/* Phone */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Phone Number
              </label>
              <input
                type="tel"
                value={formData.phone}
                onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="+1 (555) 123-4567"
              />
            </div>

            {/* Resume Upload */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Resume *
              </label>
              <div
                className={`border-2 border-dashed rounded-lg p-6 text-center cursor-pointer transition-colors ${
                  resume
                    ? 'border-green-400 bg-green-50'
                    : 'border-gray-300 hover:border-primary-400'
                }`}
                onClick={() => document.getElementById('resume-input')?.click()}
              >
                <input
                  id="resume-input"
                  type="file"
                  accept=".pdf,.doc,.docx"
                  onChange={handleFileChange}
                  className="hidden"
                />
                {resume ? (
                  <div className="flex items-center justify-center space-x-2 text-green-700">
                    <CheckCircle className="w-5 h-5" />
                    <span>{resume.name}</span>
                  </div>
                ) : (
                  <div>
                    <Upload className="w-8 h-8 text-gray-400 mx-auto mb-2" />
                    <p className="text-gray-600">Click to upload your resume</p>
                    <p className="text-sm text-gray-400 mt-1">PDF, DOC, DOCX up to 10MB</p>
                  </div>
                )}
              </div>
            </div>

            {/* Cover Letter */}
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Cover Letter (Optional)
              </label>
              <textarea
                rows={5}
                value={formData.cover_letter}
                onChange={(e) => setFormData({ ...formData, cover_letter: e.target.value })}
                className="w-full px-4 py-2 border border-gray-300 rounded-md focus:ring-2 focus:ring-primary-500 focus:border-primary-500"
                placeholder="Tell us why you're interested in this position..."
              />
            </div>

            {/* Error Message */}
            {applyMutation.isError && (
              <div className="p-4 bg-red-50 border border-red-200 rounded-md">
                <div className="flex items-center space-x-2 text-red-700">
                  <AlertCircle className="w-5 h-5" />
                  <span>Failed to submit application. Please try again.</span>
                </div>
              </div>
            )}

            {/* Submit Button */}
            <button
              type="submit"
              disabled={!resume || applyMutation.isPending}
              className="w-full py-3 px-4 bg-primary-600 text-white font-medium rounded-md hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
            >
              {applyMutation.isPending ? (
                <span className="flex items-center justify-center space-x-2">
                  <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                  <span>Submitting...</span>
                </span>
              ) : (
                'Submit Application'
              )}
            </button>
          </form>
        </div>

        {/* Footer */}
        <p className="text-center text-sm text-gray-500 mt-8">
          Powered by Smart Recruiter AI
        </p>
      </div>
    </div>
  );
}
