'use client';

import React, { useState } from 'react';
import {
  Button,
  Input,
  Select,
  Card,
  CardHeader,
  CardContent,
  CardFooter,
  Badge,
  CompletedBadge,
  InProgressBadge,
  FileUpload,
  Table,
  TableHeader,
  TableBody,
  TableRow,
  TableHead,
  TableCell,
  SearchBar,
  StatCard,
  Alert,
  Modal,
  ConfirmModal,
} from '@/components/ui';
import { Container, PageHeader } from '@/components/layout';
import {
  Plus,
  Mail,
  User,
  FileText,
  TrendingUp,
  Award,
} from 'lucide-react';

/**
 * Component showcase page for testing and documentation
 */
export default function ComponentsDemo() {
  const [selectedRubric, setSelectedRubric] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [file, setFile] = useState<File | null>(null);
  const [showModal, setShowModal] = useState(false);
  const [showConfirm, setShowConfirm] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);

  const handleFakeDelete = () => {
    setIsDeleting(true);
    // Simulates an async API call
    setTimeout(() => {
      setIsDeleting(false);
      setShowConfirm(false);
    }, 1500);
  };

  const rubricOptions = [
    {
      value: 'fullstack',
      label: 'Full-Stack Web App',
      description: 'Comprehensive evaluation for full-stack web applications',
    },
    {
      value: 'ml',
      label: 'Machine Learning Project',
      description: 'Evaluation criteria for ML/AI projects',
    },
    {
      value: 'backend',
      label: 'Backend API',
      description: 'RESTful API and backend service evaluation',
    },
  ];

  const mockData = [
    {
      id: 1,
      repository: 'student-portfolio/react-ecommerce',
      rubric: 'Full-Stack Web App',
      score: 87,
      status: 'completed',
    },
    {
      id: 2,
      repository: 'team-alpha/ml-classifier',
      rubric: 'Machine Learning Project',
      score: 92,
      status: 'completed',
    },
    {
      id: 3,
      repository: 'dev-bootcamp/api-server',
      rubric: 'Backend API',
      score: 78,
      status: 'in-progress',
    },
  ];

  return (
    <div className="min-h-screen bg-gray-50 py-12">
      <Container size="xl">
        <PageHeader
          title="UI Components Showcase"
          description="Interactive examples of all reusable components"
        />

        {/* Buttons Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Buttons</h2>
          <Card>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                <Button variant="primary">Primary</Button>
                <Button variant="secondary">Secondary</Button>
                <Button variant="outline">Outline</Button>
                <Button variant="ghost">Ghost</Button>
                <Button variant="danger">Danger</Button>
                <Button variant="primary" size="sm">
                  Small
                </Button>
                <Button variant="primary" size="lg">
                  Large
                </Button>
                <Button variant="primary" isLoading>
                  Loading
                </Button>
                <Button variant="primary" leftIcon={<Plus className="w-4 h-4" />}>
                  With Icon
                </Button>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Inputs Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Inputs</h2>
          <Card>
            <CardContent>
              <div className="space-y-4 max-w-md">
                <Input
                  label="Email"
                  type="email"
                  placeholder="you@example.com"
                  leftIcon={<Mail className="w-5 h-5" />}
                  fullWidth
                />
                <Input
                  label="Username"
                  placeholder="Enter username"
                  leftIcon={<User className="w-5 h-5" />}
                  helperText="Choose a unique username"
                  fullWidth
                />
                <Input
                  label="Repository URL"
                  placeholder="https://github.com/user/repo"
                  error="This field is required"
                  fullWidth
                />
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Select Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Select</h2>
          <Card>
            <CardContent>
              <div className="max-w-md">
                <Select
                  label="Evaluation Rubric"
                  placeholder="Select a rubric..."
                  options={rubricOptions}
                  value={selectedRubric}
                  onChange={setSelectedRubric}
                  helperText="Choose the evaluation criteria for your project"
                  fullWidth
                />
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Badges Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Badges</h2>
          <Card>
            <CardContent>
              <div className="flex flex-wrap gap-3">
                <Badge variant="success">Success</Badge>
                <Badge variant="warning">Warning</Badge>
                <Badge variant="error">Error</Badge>
                <Badge variant="info">Info</Badge>
                <Badge variant="neutral">Neutral</Badge>
                <Badge variant="success" dot>
                  With Dot
                </Badge>
                <CompletedBadge />
                <InProgressBadge />
                <Badge variant="success" size="sm">
                  Small
                </Badge>
                <Badge variant="info" size="lg">
                  Large
                </Badge>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Alerts Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Alerts</h2>
          <Card>
            <CardContent>
              <div className="space-y-4 max-w-2xl">
                <Alert
                  variant="success"
                  title="Evaluation completed"
                  message="The repository was successfully evaluated with a score of 92/100."
                />
                <Alert
                  variant="error"
                  title="Evaluation failed"
                  message="Could not reach the repository. Please check the URL and try again."
                  dismissible
                />
                <Alert
                  variant="warning"
                  message="This rubric has not been updated in over 6 months. Consider reviewing it."
                  dismissible
                />
                <Alert
                  variant="info"
                  message="Your API key will expire in 3 days. Renew it to avoid interruptions."
                  action={
                    <button className="text-sm font-medium text-blue-700 underline hover:text-blue-800">
                      Renew API key
                    </button>
                  }
                />
                <Alert
                  variant="success"
                  icon={false}
                  message="Changes saved. No icon variant."
                  dismissible
                />
              </div>
            </CardContent>
          </Card>
        </section>

        {/* File Upload Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">File Upload</h2>
          <Card>
            <CardContent>
              <div className="max-w-md">
                <FileUpload
                  label="Project Briefing (PDF)"
                  accept=".pdf"
                  maxSize={10}
                  onFileSelect={setFile}
                  helperText="Upload your project requirements document"
                />
                {file && (
                  <p className="mt-2 text-sm text-gray-600">
                    Selected: {file.name}
                  </p>
                )}
              </div>
            </CardContent>
          </Card>
        </section>

        {/* Cards Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card variant="default">
              <CardHeader title="Default Card" description="Basic card style" />
              <CardContent>
                <p>This is the default card variant with standard border.</p>
              </CardContent>
            </Card>

            <Card variant="bordered">
              <CardHeader title="Bordered Card" description="Thicker border" />
              <CardContent>
                <p>This card has a more prominent border.</p>
              </CardContent>
            </Card>

            <Card variant="elevated" hoverable>
              <CardHeader title="Elevated Card" description="With shadow" />
              <CardContent>
                <p>This card has a shadow and hover effect.</p>
              </CardContent>
              <CardFooter divided>
                <Button variant="outline" fullWidth>
                  View Details
                </Button>
              </CardFooter>
            </Card>
          </div>
        </section>

        {/* Stat Cards Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Stat Cards</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <StatCard
              title="Total Evaluations"
              value="127"
              icon={FileText}
              trend={{ value: '+12%', isPositive: true, label: 'this month' }}
            />
            <StatCard
              title="Average Score"
              value="84.5"
              icon={TrendingUp}
              trend={{ value: '+3.2 pts', isPositive: true }}
            />
            <StatCard
              title="Most Used Rubric"
              value="Full-Stack Web App"
              icon={Award}
            />
          </div>
        </section>

        {/* Search Bar Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Search Bar</h2>
          <Card>
            <CardContent>
              <SearchBar
                placeholder="Search by repository or rubric..."
                onSearch={setSearchQuery}
                fullWidth
              />
              {searchQuery && (
                <p className="mt-4 text-sm text-gray-600">
                  Searching for: <strong>{searchQuery}</strong>
                </p>
              )}
            </CardContent>
          </Card>
        </section>

        {/* Table Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Table</h2>
          <Card padding="none">
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Repository</TableHead>
                  <TableHead>Rubric</TableHead>
                  <TableHead>Score</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Actions</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {mockData.map((item) => (
                  <TableRow key={item.id} hoverable>
                    <TableCell className="font-medium">
                      {item.repository}
                    </TableCell>
                    <TableCell>{item.rubric}</TableCell>
                    <TableCell>
                      <span className="text-lg font-semibold">{item.score}</span>
                    </TableCell>
                    <TableCell>
                      {item.status === 'completed' ? (
                        <CompletedBadge />
                      ) : (
                        <InProgressBadge />
                      )}
                    </TableCell>
                    <TableCell>
                      <Button variant="ghost" size="sm">
                        View Report
                      </Button>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </Card>
        </section>

        {/* Modal Section */}
        <section className="mb-12">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Modal / Dialog</h2>
          <Card>
            <CardContent>
              <div className="flex flex-wrap gap-4">
                {/* General purpose modal */}
                <Button variant="outline" onClick={() => setShowModal(true)}>
                  Open modal
                </Button>

                {/* Confirmation / destructive action modal */}
                <Button variant="danger" onClick={() => setShowConfirm(true)}>
                  Delete rubric
                </Button>
              </div>
            </CardContent>
          </Card>
        </section>

        {/* General purpose modal */}
        <Modal
          isOpen={showModal}
          onClose={() => setShowModal(false)}
          title="Edit rubric"
          description="Update the name and criteria of this rubric."
          size="lg"
          footer={
            <>
              <Button variant="outline" onClick={() => setShowModal(false)}>Cancel</Button>
              <Button variant="primary" onClick={() => setShowModal(false)}>Save changes</Button>
            </>
          }
        >
          <div className="space-y-4">
            <Input label="Rubric name" defaultValue="Full-Stack Web App" fullWidth />
            <Input label="Description" defaultValue="Comprehensive evaluation for full-stack applications" fullWidth />
          </div>
        </Modal>

        {/* Confirmation modal */}
        <ConfirmModal
          isOpen={showConfirm}
          onClose={() => setShowConfirm(false)}
          onConfirm={handleFakeDelete}
          title="Delete rubric"
          description="This action cannot be undone."
          message='Are you sure you want to delete "Full-Stack Web App"? All evaluations using this rubric will be affected.'
          confirmLabel="Delete"
          cancelLabel="Cancel"
          confirmVariant="danger"
          isLoading={isDeleting}
        />
      </Container>
    </div>
  );
}
