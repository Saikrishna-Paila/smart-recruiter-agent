import { useQuery } from '@tanstack/react-query';
import { Link } from 'react-router-dom';
import { Briefcase, Users, CheckCircle, Clock } from 'lucide-react';
import { jobsApi } from '../api/client';

export default function Dashboard() {
  const { data: jobs, isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: () => jobsApi.list().then((res) => res.data),
  });

  const activeJobs = jobs?.filter((j: any) => j.status === 'active') || [];
  const totalApplicants = jobs?.reduce((sum: number, j: any) => sum + (j.total_applicants || 0), 0) || 0;
  const totalShortlisted = jobs?.reduce((sum: number, j: any) => sum + (j.shortlisted_count || 0), 0) || 0;

  const stats = [
    { label: 'Active Jobs', value: activeJobs.length, icon: Briefcase, color: 'bg-blue-500' },
    { label: 'Total Applicants', value: totalApplicants, icon: Users, color: 'bg-green-500' },
    { label: 'Shortlisted', value: totalShortlisted, icon: CheckCircle, color: 'bg-yellow-500' },
    { label: 'Pending Review', value: totalApplicants - totalShortlisted, icon: Clock, color: 'bg-purple-500' },
  ];

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Dashboard</h1>
        <p className="text-gray-600">Overview of your recruitment pipeline</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {stats.map((stat) => {
          const Icon = stat.icon;
          return (
            <div key={stat.label} className="bg-white rounded-lg shadow p-6">
              <div className="flex items-center">
                <div className={`${stat.color} rounded-lg p-3`}>
                  <Icon className="w-6 h-6 text-white" />
                </div>
                <div className="ml-4">
                  <p className="text-sm text-gray-500">{stat.label}</p>
                  <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
                </div>
              </div>
            </div>
          );
        })}
      </div>

      {/* Active Jobs */}
      <div className="bg-white rounded-lg shadow">
        <div className="px-6 py-4 border-b flex justify-between items-center">
          <h2 className="text-lg font-semibold text-gray-900">Active Positions</h2>
          <Link
            to="/jobs/new"
            className="text-primary-600 hover:text-primary-700 text-sm font-medium"
          >
            + Create New
          </Link>
        </div>
        <div className="divide-y">
          {activeJobs.length === 0 ? (
            <div className="px-6 py-8 text-center text-gray-500">
              No active jobs. Create your first job posting!
            </div>
          ) : (
            activeJobs.map((job: any) => (
              <Link
                key={job.id}
                to={`/jobs/${job.id}`}
                className="block px-6 py-4 hover:bg-gray-50 transition-colors"
              >
                <div className="flex justify-between items-center">
                  <div>
                    <h3 className="font-medium text-gray-900">{job.title}</h3>
                    <p className="text-sm text-gray-500">
                      {job.department} • {job.location}
                    </p>
                  </div>
                  <div className="flex items-center space-x-6 text-sm">
                    <div className="text-center">
                      <p className="font-semibold text-gray-900">{job.total_applicants}</p>
                      <p className="text-gray-500">Applied</p>
                    </div>
                    <div className="text-center">
                      <p className="font-semibold text-gray-900">{job.screened_count}</p>
                      <p className="text-gray-500">Screened</p>
                    </div>
                    <div className="text-center">
                      <p className="font-semibold text-gray-900">{job.shortlisted_count}</p>
                      <p className="text-gray-500">Shortlisted</p>
                    </div>
                  </div>
                </div>
              </Link>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
