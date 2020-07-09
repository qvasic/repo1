pipeline
{
	agent any
	stages
	{
		stage('build')
		{
			steps
			{
				echo building...
				make app
			}
		}
		stage('test')
		{
			steps
			{
				echo testing...
				make test
			}
		}
	}
}
