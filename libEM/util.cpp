/**
 * $Id$
 */
#include "byteorder.h"
#include "Assert.h"
#include "emconstants.h"
#include "emdata.h"

#include <string.h>
#include <fcntl.h>
#include <time.h>
#include <iomanip>
#include <sstream>

#include <gsl/gsl_sf_bessel.h>
#include <sys/types.h>
#include <gsl/gsl_sf_bessel.h>
#include <algorithm>

#ifndef WIN32
	#include <unistd.h>
	#include <sys/param.h>
#else
	#include <io.h>
	#define access _access
	#define F_OK 00
#endif  //WIN32

using namespace std;
using namespace boost;
using namespace EMAN;

void Util::ap2ri(float *data, size_t n)
{
	Assert(n > 0);

	if (!data) {
		throw NullPointerException("pixel data array");
	}

	for (size_t i = 0; i < n; i += 2) {
		float f = data[i] * sin(data[i + 1]);
		data[i] = data[i] * cos(data[i + 1]);
		data[i + 1] = f;
	}
}

void Util::flip_complex_phase(float *data, size_t n)
{
	Assert(n > 0);

	if (!data) {
		throw NullPointerException("pixel data array");
	}

	for (size_t i = 0; i < n; i += 2) {
		data[i + 1] *= -1;
	}
}

int Util::file_lock_wait(FILE * file)
{
#ifdef WIN32
	return 1;
#else

	if (!file) {
		throw NullPointerException("Tried to lock NULL file");
	}

	int fdes = fileno(file);

	struct flock fl;
	fl.l_type = F_WRLCK;
	fl.l_whence = SEEK_SET;
	fl.l_start = 0;
	fl.l_len = 0;
#ifdef WIN32
	fl.l_pid = _getpid();
#else
	fl.l_pid = getpid();
#endif

#if defined __sgi
	fl.l_sysid = getpid();
#endif

	int err = 0;
	if (fcntl(fdes, F_SETLKW, &fl) == -1) {
		LOGERR("file locking error! NFS problem?");

		int i = 0;
		for (i = 0; i < 5; i++) {
			if (fcntl(fdes, F_SETLKW, &fl) != -1) {
				break;
			}
			else {
#ifdef WIN32
				Sleep(1000);
#else
				sleep(1);
#endif

			}
		}
		if (i == 5) {
			LOGERR("Fatal file locking error");
			err = 1;
		}
	}

	return err;
#endif
}



bool Util::check_file_by_magic(const void *first_block, const char *magic)
{
	if (!first_block || !magic) {
		throw NullPointerException("first_block/magic");
	}

	const char *buf = static_cast < const char *>(first_block);

	if (strncmp(buf, magic, strlen(magic)) == 0) {
		return true;
	}
	return false;
}

bool Util::is_file_exist(const string & filename)
{
	if (access(filename.c_str(), F_OK) == 0) {
		return true;
	}
	return false;
}


void Util::flip_image(float *data, size_t nx, size_t ny)
{
	if (!data) {
		throw NullPointerException("image data array");
	}
	Assert(nx > 0);
	Assert(ny > 0);

	float *buf = new float[nx];
	size_t row_size = nx * sizeof(float);

	for (size_t i = 0; i < ny / 2; i++) {
		memcpy(buf, &data[i * nx], row_size);
		memcpy(&data[i * nx], &data[(ny - 1 - i) * nx], row_size);
		memcpy(&data[(ny - 1 - i) * nx], buf, row_size);
	}

	if( buf )
	{
		delete[]buf;
		buf = 0;
	}
}

bool Util::sstrncmp(const char *s1, const char *s2)
{
	if (!s1 || !s2) {
		throw NullPointerException("Null string");
	}

	if (strncmp(s1, s2, strlen(s2)) == 0) {
		return true;
	}

	return false;
}

string Util::int2str(int n)
{
	char s[32] = {'\0'};
	sprintf(s, "%d", n);
	return string(s);
}

string Util::get_line_from_string(char **slines)
{
	if (!slines || !(*slines)) {
		throw NullPointerException("Null string");
	}

	string result = "";
	char *str = *slines;

	while (*str != '\n' && *str != '\0') {
		result.push_back(*str);
		str++;
	}
	if (*str != '\0') {
		str++;
	}
	*slines = str;

	return result;
}



bool Util::get_str_float(const char *s, const char *float_var, float *p_val)
{
	if (!s || !float_var || !p_val) {
		throw NullPointerException("string float");
	}
	size_t n = strlen(float_var);
	if (strncmp(s, float_var, n) == 0) {
		*p_val = (float) atof(&s[n]);
		return true;
	}

	return false;
}

bool Util::get_str_float(const char *s, const char *float_var, float *p_v1, float *p_v2)
{
	if (!s || !float_var || !p_v1 || !p_v2) {
		throw NullPointerException("string float");
	}

	size_t n = strlen(float_var);
	if (strncmp(s, float_var, n) == 0) {
		sscanf(&s[n], "%f,%f", p_v1, p_v2);
		return true;
	}

	return false;
}

bool Util::get_str_float(const char *s, const char *float_var,
						 int *p_v0, float *p_v1, float *p_v2)
{
	if (!s || !float_var || !p_v0 || !p_v1 || !p_v2) {
		throw NullPointerException("string float");
	}

	size_t n = strlen(float_var);
	*p_v0 = 0;
	if (strncmp(s, float_var, n) == 0) {
		if (s[n] == '=') {
			*p_v0 = 2;
			sscanf(&s[n + 1], "%f,%f", p_v1, p_v2);
		}
		else {
			*p_v0 = 1;
		}
		return true;
	}
	return false;
}

bool Util::get_str_int(const char *s, const char *int_var, int *p_val)
{
	if (!s || !int_var || !p_val) {
		throw NullPointerException("string int");
	}

	size_t n = strlen(int_var);
	if (strncmp(s, int_var, n) == 0) {
		*p_val = atoi(&s[n]);
		return true;
	}
	return false;
}

bool Util::get_str_int(const char *s, const char *int_var, int *p_v1, int *p_v2)
{
	if (!s || !int_var || !p_v1 || !p_v2) {
		throw NullPointerException("string int");
	}

	size_t n = strlen(int_var);
	if (strncmp(s, int_var, n) == 0) {
		sscanf(&s[n], "%d,%d", p_v1, p_v2);
		return true;
	}
	return false;
}

bool Util::get_str_int(const char *s, const char *int_var, int *p_v0, int *p_v1, int *p_v2)
{
	if (!s || !int_var || !p_v0 || !p_v1 || !p_v2) {
		throw NullPointerException("string int");
	}

	size_t n = strlen(int_var);
	*p_v0 = 0;
	if (strncmp(s, int_var, n) == 0) {
		if (s[n] == '=') {
			*p_v0 = 2;
			sscanf(&s[n + 1], "%d,%d", p_v1, p_v2);
		}
		else {
			*p_v0 = 1;
		}
		return true;
	}
	return false;
}

string Util::change_filename_ext(const string & old_filename,
								 const string & ext)
{
	Assert(old_filename != "");
	if (ext == "") {
		return old_filename;
	}

	string filename = old_filename;
	size_t dot_pos = filename.rfind(".");
	if (dot_pos != string::npos) {
		filename = filename.substr(0, dot_pos+1);
	}
	else {
		filename = filename + ".";
	}
	filename = filename + ext;
	return filename;
}

string Util::remove_filename_ext(const string& filename)
{
    if (filename == "") {
        return "";
    }

	char *buf = new char[filename.size()+1];
	strcpy(buf, filename.c_str());
	char *old_ext = strrchr(buf, '.');
	if (old_ext) {
		buf[strlen(buf) - strlen(old_ext)] = '\0';
	}
	string result = string(buf);
	if( buf )
	{
		delete [] buf;
		buf = 0;
	}
	return result;
}

string Util::sbasename(const string & filename)
{
    if (filename == "") {
        return "";
    }

	char s = '/';
#ifdef WIN32
	s = '\\';
#endif
	char * c = strrchr(filename.c_str(), s);
    if (!c) {
        return filename;
    }
	else {
		c++;
	}
    return string(c);
}


string Util::get_filename_ext(const string& filename)
{
    if (filename == "") {
        return "";
    }

	string result = "";
	char *ext = strrchr(filename.c_str(), '.');
	if (ext) {
		ext++;
		result = string(ext);
	}
	return result;
}



void Util::calc_least_square_fit(size_t nitems, const float *data_x, const float *data_y,
								 float *slope, float *intercept, bool ignore_zero)
{
	Assert(nitems > 0);

	if (!data_x || !data_y || !slope || !intercept) {
		throw NullPointerException("null float pointer");
	}
	double sum = 0;
	double sum_x = 0;
	double sum_y = 0;
	double sum_xx = 0;
	double sum_xy = 0;

	for (size_t i = 0; i < nitems; i++) {
		if (!ignore_zero || (data_x[i] != 0 && data_y[i] != 0)) {
			double y = data_y[i];
			double x = i;
			if (data_x) {
				x = data_x[i];
			}

			sum_x += x;
			sum_y += y;
			sum_xx += x * x;
			sum_xy += x * y;
			sum++;
		}
	}

	double div = sum * sum_xx - sum_x * sum_x;
	if (div == 0) {
		div = 0.0000001f;
	}

	*intercept = (float) ((sum_xx * sum_y - sum_x * sum_xy) / div);
	*slope = (float) ((sum * sum_xy - sum_x * sum_y) / div);
}

void Util::save_data(const vector < float >&x_array, const vector < float >&y_array,
					 const string & filename)
{
	Assert(x_array.size() > 0);
	Assert(y_array.size() > 0);
	Assert(filename != "");

	if (x_array.size() != y_array.size()) {
		LOGERR("array x and array y have different size: %d != %d\n",
			   x_array.size(), y_array.size());
		return;
	}

	FILE *out = fopen(filename.c_str(), "wb");
	if (!out) {
		throw FileAccessException(filename);
	}

	for (size_t i = 0; i < x_array.size(); i++) {
		fprintf(out, "%g\t%g\n", x_array[i], y_array[i]);
	}
	fclose(out);
}

void Util::save_data(float x0, float dx, const vector < float >&y_array,
					 const string & filename)
{
	Assert(dx != 0);
	Assert(y_array.size() > 0);
	Assert(filename != "");

	FILE *out = fopen(filename.c_str(), "wb");
	if (!out) {
		throw FileAccessException(filename);
	}

	for (size_t i = 0; i < y_array.size(); i++) {
		fprintf(out, "%g\t%g\n", x0 + dx * i, y_array[i]);
	}
	fclose(out);
}


void Util::save_data(float x0, float dx, float *y_array,
					 size_t array_size, const string & filename)
{
	Assert(dx > 0);
	Assert(array_size > 0);
	Assert(filename != "");

	if (!y_array) {
		throw NullPointerException("y array");
	}

	FILE *out = fopen(filename.c_str(), "wb");
	if (!out) {
		throw FileAccessException(filename);
	}

	for (size_t i = 0; i < array_size; i++) {
		fprintf(out, "%g\t%g\n", x0 + dx * i, y_array[i]);
	}
	fclose(out);
}


void Util::spline_mat(float *x, float *y, int n,  float *xq, float *yq, int m) //PRB
{

	float x0= x[0];
	float x1= x[1];
	float x2= x[2];
	float y0= y[0];
	float y1= y[1];
	float y2= y[2];
	float yp1 =  (y1-y0)/(x1-x0) +  (y2-y0)/(x2-x0) - (y2-y1)/(x2-x1)  ;
	float xn  = x[n];
	float xnm1= x[n-1];
	float xnm2= x[n-2];
	float yn  = y[n];
	float ynm1= y[n-1];
	float ynm2= y[n-2];
	float ypn=  (yn-ynm1)/(xn-xnm1) +  (yn-ynm2)/(xn-xnm2) - (ynm1-ynm2)/(xnm1-xnm2) ;
	float *y2d = new float[n];
	Util::spline(x,y,n,yp1,ypn,y2d);
	Util::splint(x,y,y2d,n,xq,yq,m); //PRB
	delete [] y2d;
	return;
}


void Util::spline(float *x, float *y, int n, float yp1, float ypn, float *y2) //PRB
{
	int i,k;
	float p, qn, sig, un, *u;
	u=new float[n-1];

	if (yp1 > .99e30){
		y2[0]=u[0]=0.0;
	}else{
		y2[0]=-.5f;
		u[0] =(3.0f/ (x[1] -x[0]))*( (y[1]-y[0])/(x[1]-x[0]) -yp1);
	}

	for (i=1; i < n-1; i++) {
		sig= (x[i] - x[i-1])/(x[i+1] - x[i-1]);
		p = sig*y2[i-1] + 2.0f;
		y2[i]  = (sig-1.0f)/p;
		u[i] = (y[i+1] - y[i] )/(x[i+1]-x[i] ) -  (y[i] - y[i-1] )/(x[i] -x[i-1]);
		u[i] = (6.0f*u[i]/ (x[i+1]-x[i-1]) - sig*u[i-1])/p;
	}

	if (ypn>.99e30){
		qn=0; un=0;
	} else {
		qn= .5f;
		un= (3.0f/(x[n-1] -x[n-2])) * (ypn -  (y[n-1]-y[n-2])/(x[n-1]-x[n-2]));
	}
	y2[n-1]= (un - qn*u[n-2])/(qn*y2[n-2]+1.0f);
	for (k=n-2; k>=0; k--){
		y2[k]=y2[k]*y2[k+1]+u[k];
	}
	delete [] u;
}

void Util::splint( float *xa, float *ya, float *y2a, int n,  float *xq, float *yq, int m) //PRB
{
	int klo, khi, k;
	float h, b, a;

//	klo=0; // can try to put here
	for (int j=0; j<m;j++){
		klo=0;
		khi=n-1;
		while (khi-klo >1) {
			k=(khi+klo) >>1;
			if  (xa[k]>xq[j]){ khi=k;}
			else { klo=k;}
		}
		h=xa[khi]- xa[klo];
		if (h==0.0) printf("Bad XA input to routine SPLINT \n");
		a =(xa[khi]-xq[j])/h;
		b=(xq[j]-xa[klo])/h;
		yq[j]=a*ya[klo] + b*ya[khi]
			+ ((a*a*a-a)*y2a[klo]
			     +(b*b*b-b)*y2a[khi]) *(h*h)/6.0f;
	}
//	printf("h=%f, a = %f, b=%f, ya[klo]=%f, ya[khi]=%f , yq=%f\n",h, a, b, ya[klo], ya[khi],yq[0]);
}


void Util::sort_mat(float *left, float *right, int *leftPerm, int *rightPerm)
// Adapted by PRB from a macro definition posted on SourceForge by evildave
{
	float *pivot ; int *pivotPerm;

	{
		float *pLeft  =   left; int *pLeftPerm  =  leftPerm;
		float *pRight =  right; int *pRightPerm = rightPerm;
		float scratch =  *left; int scratchPerm = *leftPerm;

		while (pLeft < pRight) {
			while ((*pRight > scratch) && (pLeft < pRight)) {
				pRight--; pRightPerm--;
			}
			if (pLeft != pRight) {
				*pLeft = *pRight; *pLeftPerm = *pRightPerm;
				pLeft++; pLeftPerm++;
			}
			while ((*pLeft < scratch) && (pLeft < pRight)) {
				pLeft++; pLeftPerm++;
			}
			if (pLeft != pRight) {
				*pRight = *pLeft; *pRightPerm = *pLeftPerm;
				pRight--; pRightPerm--;
			}
		}
		*pLeft = scratch; *pLeftPerm = scratchPerm;
		pivot = pLeft; pivotPerm= pLeftPerm;
	}
	if (left < pivot) {
		sort_mat(left, pivot - 1,leftPerm,pivotPerm-1);
	}
	if (right > pivot) {
		sort_mat(pivot + 1, right,pivotPerm+1,rightPerm);
	}
}

void Util::Radialize(int *PermMatTr, float *kValsSorted,   // PRB
               float *weightofkValsSorted, int Size, int *SizeReturned)
{
	int iMax = (int) floor( (Size-1.0)/2 +.01);
	int CountMax = (iMax+2)*(iMax+1)/2;
	int Count=-1;
	float *kVals     = new float[CountMax];
	float *weightMat = new float[CountMax];
	int *PermMat     = new   int[CountMax];
	SizeReturned[0] = CountMax;

//	printf("Aa \n");	fflush(stdout);
	for (int jkx=0; jkx< iMax+1; jkx++) {
		for (int jky=0; jky< jkx+1; jky++) {
			Count++;
			kVals[Count] = sqrtf((float) (jkx*jkx +jky*jky));
			weightMat[Count]=  1.0;
			if (jkx!=0)  { weightMat[Count] *=2;}
			if (jky!=0)  { weightMat[Count] *=2;}
			if (jkx!=jky){ weightMat[Count] *=2;}
			PermMat[Count]=Count+1;
	}}

	int lkVals = Count+1;
//	printf("Cc \n");fflush(stdout);

	sort_mat(&kVals[0],&kVals[Count],
	     &PermMat[0],  &PermMat[Count]);  //PermMat is
				//also returned as well as kValsSorted
	fflush(stdout);

	int newInd;

        for (int iP=0; iP < lkVals ; iP++ ) {
		newInd =  PermMat[iP];
		PermMatTr[newInd-1] = iP+1;
	}

//	printf("Ee \n"); fflush(stdout);

	int CountA=-1;
	int CountB=-1;

	while (CountB< (CountMax-1)) {
		CountA++;
		CountB++;
//		printf("CountA=%d ; CountB=%d \n", CountA,CountB);fflush(stdout);
		kValsSorted[CountA] = kVals[CountB] ;
		if (CountB<(CountMax-1) ) {
			while (fabs(kVals[CountB] -kVals[CountB+1])<.0000001  ) {
				SizeReturned[0]--;
				for (int iP=0; iP < lkVals; iP++){
//					printf("iP=%d \n", iP);fflush(stdout);
					if  (PermMatTr[iP]>CountA+1) {
						PermMatTr[iP]--;
		    			}
		 		}
				CountB++;
	    		}
		}
	}
	

	for (int CountD=0; CountD < CountMax; CountD++) {
	    newInd = PermMatTr[CountD];
	    weightofkValsSorted[newInd-1] += weightMat[CountD];
        }

}

float Util::get_frand(int lo, int hi)
{
	return get_frand((float)lo, (float)hi);
}

float Util::get_frand(float lo, float hi)
{
	static bool inited = false;
	if (!inited) {
		srand(time(0));
		inited = true;
	}

	float r = (hi - lo) * rand() / (RAND_MAX + 1.0f) + lo;
	return r;
}

float Util::get_frand(double lo, double hi)
{
	static bool inited = false;
	if (!inited) {
		srand(time(0));
		inited = true;
	}

	double r = (hi - lo) * rand() / (RAND_MAX + 1.0) + lo;
	return (float)r;
}

float Util::get_gauss_rand(float mean, float sigma)
{
	float x = 0;
	float r = 0;
	bool valid = true;

	while (valid) {
		x = get_frand(-1.0, 1.0);
		float y = get_frand(-1.0, 1.0);
		r = x * x + y * y;

		if (r <= 1.0 && r > 0) {
			valid = false;
		}
	}

	float f = sqrt(-2.0f * log(r) / r);
	float result = x * f * sigma + mean;
	return result;
}

void Util::find_max(const float *data, size_t nitems, float *max_val, int *max_index)
{
	Assert(nitems > 0);

	if (!data || !max_val || !max_index) {
		throw NullPointerException("data/max_val/max_index");
	}
	float max = -FLT_MAX;
	int m = 0;

	for (size_t i = 0; i < nitems; i++) {
		if (data[i] > max) {
			max = data[i];
			m = (int)i;
		}
	}

	*max_val = (float)m;

	if (max_index) {
		*max_index = m;
	}
}

void Util::find_min_and_max(const float *data, size_t nitems,
							float *max_val, float *min_val,
							int *max_index, int *min_index)
{
	Assert(nitems > 0);

	if (!data || !max_val || !min_val || !max_index || !min_index) {
		throw NullPointerException("data/max_val/min_val/max_index/min_index");
	}
	float max = -FLT_MAX;
	float min = FLT_MAX;
	int max_i = 0;
	int min_i = 0;

	for (size_t i = 0; i < nitems; i++) {
		if (data[i] > max) {
			max = data[i];
			max_i = (int)i;
		}
		if (data[i] < min) {
			min = data[i];
			min_i = (int)i;
		}
	}

	*max_val = max;
	*min_val = min;

	if (min_index) {
		*min_index = min_i;
	}

	if (max_index) {
		*max_index = max_i;
	}

}



int Util::calc_best_fft_size(int low)
{
	Assert(low >= 0);

	//array containing valid sizes <1024 for speed
	static char *valid = NULL;

	if (!valid) {
		valid = (char *) calloc(4096, 1);

		for (float i2 = 1; i2 < 12.0; i2 += 1.0) {

			float f1 = pow((float) 2.0, i2);
			for (float i3 = 0; i3 < 8.0; i3 += 1.0) {

				float f2 = pow((float) 3.0, i3);
				for (float i5 = 0; i5 < 6.0; i5 += 1.0) {

					float f3 = pow((float) 5.0, i5);
					for (float i7 = 0; i7 < 5.0; i7 += 1.0) {

						float f = f1 * f2 * f3 * pow((float) 7.0, i7);
						if (f <= 4095.0) {
							int n = (int) f;
							valid[n] = 1;
						}
					}
				}
			}
		}
	}

	for (int i = low; i < 4096; i++) {
		if (valid[i]) {
			return i;
		}
	}

	LOGERR("Sorry, can only find good fft sizes up to 4096 right now.");

	return 1;
}

string Util::get_time_label()
{
	time_t t0 = time(0);
	struct tm *t = localtime(&t0);
	char label[32];
	sprintf(label, "%d/%02d/%04d %d:%02d",
			t->tm_mon + 1, t->tm_mday, t->tm_year + 1900, t->tm_hour, t->tm_min);
	return string(label);
}


void Util::set_log_level(int argc, char *argv[])
{
	if (argc > 1 && strncmp(argv[1], "-v", 2) == 0) {
		char level_str[32];
		strcpy(level_str, argv[1] + 2);
		Log::LogLevel log_level = (Log::LogLevel) atoi(level_str);
		Log::logger()->set_level(log_level);
	}
}

void Util::printMatI3D(MIArray3D& mat, const string str, ostream& out) {
	// Note: Don't need to check if 3-D because 3D is part of
	//       the MIArray3D typedef.
	out << "Printing 3D Integer data: " << str << std::endl;
	const multi_array_types::size_type* sizes = mat.shape();
	int nx = sizes[0], ny = sizes[1], nz = sizes[2];
	const multi_array_types::index* indices = mat.index_bases();
	int bx = indices[0], by = indices[1], bz = indices[2];
	for (int iz = bz; iz < nz+bz; iz++) {
		cout << "(z = " << iz << " slice)" << endl;
		for (int ix = bx; ix < nx+bx; ix++) {
			for (int iy = by; iy < ny+by; iy++) {
				cout << setiosflags(ios::fixed) << setw(5)
					 << mat[ix][iy][iz] << "  ";
			}
			cout << endl;
		}
	}
}

vector<float>
Util::voea(float delta, float t1, float t2, float p1, float p2)
{
	vector<float> angles;
	float psi = 0.0;
	if ((0.0 == t1)&&(0.0 == t2)||(t1 >= t2)) {
		t1 = 0.0f;
		t2 = 90.0f;
	}
	if ((0.0 == p1)&&(0.0 == p2)||(p1 >= p2)) {
		p1 = 0.0f;
		p2 = 359.9f;
	}
	bool skip = ((t1 < 90.0)&&(90.0 == t2)&&(0.0 == p1)&&(p2 > 180.0));
	for (float theta = t1; theta <= t2; theta += delta) {
		float detphi;
		int lt;
		if ((0.0 == theta)||(180.0 == theta)) {
			detphi = 360.0f;
			lt = 1;
		} else {
			detphi = delta/sin(theta*static_cast<float>(dgr_to_rad));
			lt = int((p2 - p1)/detphi)-1;
			if (lt < 1) lt = 1;
			detphi = (p2 - p1)/lt;
		}
		for (int i = 0; i < lt; i++) {
			float phi = p1 + i*detphi;
			if (skip&&(90.0 == theta)&&(phi > 180.0)) continue;
			angles.push_back(phi);
			angles.push_back(theta);
			angles.push_back(psi);
		}
	}
	return angles;
}


float Util::triquad(double r, double s, double t, float f[]) {
	const float c2 = 1.0f / 2.0f;
	const float c4 = 1.0f / 4.0f;
	const float c8 = 1.0f / 8.0f;
	float rs = (float)(r*s);
	float st = (float)(s*t);
	float rt = (float)(r*t);
	float rst = (float)(r*st);
	float rsq = (float)(1 - r*r);
	float ssq = (float)(1 - s*s);
	float tsq = (float)(1 - t*t);
	float rm1 = (float)(1 - r);
	float sm1 = (float)(1 - s);
	float tm1 = (float)(1 - t);
	float rp1 = (float)(1 + r);
	float sp1 = (float)(1 + s);
	float tp1 = (float)(1 + t);

	return (float)(
		(-c8) * rst * rm1  * sm1  * tm1 * f[ 0] +
		( c4) * st	* rsq  * sm1  * tm1 * f[ 1] +
		( c8) * rst * rp1  * sm1  * tm1 * f[ 2] +
		( c4) * rt	* rm1  * ssq  * tm1 * f[ 3] +
		(-c2) * t	* rsq  * ssq  * tm1 * f[ 4] +
		(-c4) * rt	* rp1  * ssq  * tm1 * f[ 5] +
		( c8) * rst * rm1  * sp1  * tm1 * f[ 6] +
		(-c4) * st	* rsq  * sp1  * tm1 * f[ 7] +
		(-c8) * rst * rp1  * sp1  * tm1 * f[ 8] +

		( c4) * rs	* rm1  * sm1  * tsq * f[ 9] +
		(-c2) * s	* rsq  * sm1  * tsq * f[10] +
		(-c4) * rs	* rp1  * sm1  * tsq * f[11] +
		(-c2) * r	* rm1  * ssq  * tsq * f[12] +
					  rsq  * ssq  * tsq * f[13] +
		( c2) * r	* rp1  * ssq  * tsq * f[14] +
		(-c4) * rs	* rm1  * sp1  * tsq * f[15] +
		( c2) * s	* rsq  * sp1  * tsq * f[16] +
		( c4) * rs	* rp1  * sp1  * tsq * f[17] +

		( c8) * rst * rm1  * sm1  * tp1 * f[18] +
		(-c4) * st	* rsq  * sm1  * tp1 * f[19] +
		(-c8) * rst * rp1  * sm1  * tp1 * f[20] +
		(-c4) * rt	* rm1  * ssq  * tp1 * f[21] +
		( c2) * t	* rsq  * ssq  * tp1 * f[22] +
		( c4) * rt	* rp1  * ssq  * tp1 * f[23] +
		(-c8) * rst * rm1  * sp1  * tp1 * f[24] +
		( c4) * st	* rsq  * sp1  * tp1 * f[25] +
		( c8) * rst * rp1  * sp1  * tp1 * f[26]);
}

float Util::quadri(EMData* image, float x, float y, int zslice) {
	// sanity check
	if (image->get_ysize() <= 1) {
		throw ImageDimensionException("Interpolated image must be at least 2D");
	}
	int nx = image->get_xsize();
	int ny = image->get_ysize();
	MArray3D fdata = image->get_3dview();
	// periodic boundary conditions
	x -= Util::round((x/float(nx))-0.5f)*nx; // x in [0,nx-1]
	// zero is a bit of a problem
	if (x == nx) x = 0.f;
	y -= Util::round((y/float(ny))-0.5f)*ny; // y in [0,ny-1]
	if (y == ny) y = 0.f;
	int ix = int(x);
	int ixp = ix + 1;
	if (ixp > nx-1) ixp -= nx;
	int ixm = ix - 1;
	if (ixm < 0) ixm += nx;
	float p = x - float(ix);
	int iy = int(y);
	int iyp = iy + 1;
	if (iyp > ny-1) iyp -= ny;
	int iym = iy - 1;
	if (iym < 0) iym += ny;
	float q = y - float(iy);
	float f00 = fdata[ix][iy][zslice];
	float f0p = fdata[ix][iyp][zslice];
	float fp0 = fdata[ixp][iy][zslice];
	float f0m = fdata[ix][iym][zslice];
	float fm0 = fdata[ixm][iy][zslice];
	float fpp = fdata[ixp][iyp][zslice];
	float c1 = fp0 - f00;
	float c2 = 0.5f*(c1 - f00 + fm0);
	float c3 = f0p - f00;
	float c4 = 0.5f*(c3 - f00 + f0m);
	float c5 = fpp - f00 - c1 - c3;
	float result = f00 
		         + p*(c1 + (p-1)*c2 + q*c5)
				 + q*(c3 + (q-1)*c4);
	return result;
}

Util::KaiserBessel::KaiserBessel(float alpha_, int K_, float r_, float v_,
		                         int N_, float vtable_, int ntable_) 
		: alpha(alpha_), v(v_), r(r_), N(N_), K(K_), vtable(vtable_), 
		  ntable(ntable_) {
	// Default values are alpha=1.25, K=6, r=0.5, v = K/2
	if (0.f == v) v = float(K)/2;
	if (0.f == vtable) vtable = v;
	fac = static_cast<float>(twopi)*alpha*r*v;
	alphar = alpha*r;
	vadjust = 1.1f*v;
	facadj = twopi*alpha*r*vadjust;
	build_I0table();
}

float Util::KaiserBessel::i0win(float x) const {
#if 0 // comment out I0-based in favor of I1-based
	float val0 = static_cast<float>(gsl_sf_bessel_I0(fac))/(2.0f*v);
	float absx = fabs(x);
	if (absx > v) return 0.f;
	float rt = sqrt(1.f - pow(x/v,2));
	return gsl_sf_bessel_I0(fac*rt)/(2*v)/val0;
#endif // 0
	//float val0 = sqrt(facadj)*float(gsl_sf_bessel_I1(facadj));
	float val0 = float(gsl_sf_bessel_I0(facadj));
	//float val0 = gsl_sf_bessel_I1(facadj);
	float absx = fabs(x);
	if (absx > vadjust) return 0.f;
	float rt = sqrt(1.f - pow(absx/vadjust, 2));
	//float res = sqrt(facadj*rt)*float(gsl_sf_bessel_I1(facadj*rt))/val0;
	float res = float(gsl_sf_bessel_I0(facadj*rt))/val0;
	//float res = rt*float(gsl_sf_bessel_I1(facadj*rt))/val0;
	return res;
}

void Util::KaiserBessel::build_I0table() {
	i0table.resize(ntable+1); // i0table[0:ntable]
	int ltab = int(round(float(ntable)/1.1f));
	fltb = float(ltab)/(K/2);
	float val0 = sqrt(facadj)*gsl_sf_bessel_I1(facadj);
	//float val0 = gsl_sf_bessel_I0(facadj);
	//float val0 = gsl_sf_bessel_I1(facadj);
	for (int i=ltab+1; i <= ntable; i++) i0table[i] = 0.f;
	for (int i=0; i <= ltab; i++) {
		float s = float(i)/fltb/N;
		if (s < vadjust) {
			float rt = sqrt(1.f - pow(s/vadjust, 2));
			i0table[i] = sqrt(facadj*rt)*gsl_sf_bessel_I1(facadj*rt)/val0;
			//i0table[i] = gsl_sf_bessel_I0(facadj*rt)/val0;
			//i0table[i] = rt*gsl_sf_bessel_I1(facadj*rt)/val0;
		} else {
			i0table[i] = 0.f;
		}
#if 0 // old version
	dtable = vtable / ntable;
	float vratio = v/vtable;
	for (int i=0; i <= ntable; i++) {
		float x = i*dtable;
		i0table[i] = i0win(x*vratio);
#endif // 0
	}
}

float Util::KaiserBessel::I0table_maxerror() {
	float maxdiff = 0.f;
	for (int i = 1; i <= ntable; i++) {
		float diff = fabs(i0table[i] - i0table[i-1]);
		if (diff > maxdiff) maxdiff = diff;
	}
	return maxdiff;
}

float Util::KaiserBessel::sinhwin(float x) const {
	float val0 = sinh(fac)/fac;
	float absx = fabs(x);
	if (0.0 == x) {
		float res = 1.0f;
		return res;
	} else if (absx == alphar) {
		return 1.0f/val0;
	} else if (absx < alphar) {
		float rt = sqrt(1.0f - pow((x/alphar), 2));
		float facrt = fac*rt;
		float res = (sinh(facrt)/facrt)/val0;
		return res;
	} else {
		float rt = sqrt(pow((x/alphar),2) - 1.f);
		float facrt = fac*rt;
		float res = (sin(facrt)/facrt)/val0;
		return res;
	}
}

#if 0 // 1-st order KB window
float Util::KaiserBessel::sinhwin(float x) const {
	//float val0 = sinh(fac)/fac;
	float prefix = 2*facadj*vadjust/float(gsl_sf_bessel_I1(facadj));
	float val0 = prefix*(cosh(facadj) - sinh(facadj)/facadj);
	float absx = fabs(x);
	if (0.0 == x) {
		//float res = 1.0f;
		float res = val0;
		return res;
	} else if (absx == alphar) {
		//return 1.0f/val0;
		return prefix;
	} else if (absx < alphar) {
		float rt = sqrt(1.0f - pow((x/alphar), 2));
		//float facrt = fac*rt;
		float facrt = facadj*rt;
		//float res = (sinh(facrt)/facrt)/val0;
		float res = prefix*(cosh(facrt) - sinh(facrt)/facrt);
		return res;
	} else {
		float rt = sqrt(pow((x/alphar),2) - 1.f);
		//float facrt = fac*rt;
		float facrt = facadj*rt;
		//float res = (sin(facrt)/facrt)/val0;
		float res = prefix*(sin(facrt)/facrt - cos(facrt));
		return res;
	}
}

#endif // 0

/* vim: set ts=4 noet: */
