pipeline
{
	agent any
	stages
	{
		stage('build')
		{
			steps
			{
				echo 'building...'
				sh 'cd jenkins-test-proj && make app'
			}
		}
		stage('test')
		{
			steps
			{
				echo 'testing...'
				sh 'cd jenkins-test-proj && make test'
			}
		}
	}
}
